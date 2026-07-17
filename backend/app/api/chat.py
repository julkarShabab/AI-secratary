import json
import asyncio
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.llm.groq_llm import GroqLLM
from app.agents.orchestrator import Orchestrator
from app.memory.memory_manager import MemoryManager
from app.tools.email_tool import EmailTool
from app.tools.calendar_tool import CalendarTool
from app.tools.search_tool import SearchTool
from app.tools.slack_tool import SlackTool
from app.tools.task_tool import TaskTool
from app.db.session import SessionLocal
from app.db import models
from app.core.security import decode_access_token
from datetime import datetime, timezone

router = APIRouter()

with open("app/prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()


def get_tools(user_id: int, db):
    tool_factories = [
        lambda: EmailTool(user_id=user_id, db=db),
        lambda: CalendarTool(user_id=user_id, db=db),
        lambda: SearchTool(),
        lambda: SlackTool(),
        lambda: TaskTool(),
    ]
    tools = []
    for make_tool in tool_factories:
        try:
            tools.append(make_tool())
        except Exception as e:
            print(f"[get_tools] Skipping a tool, failed to init: {e}")
    return tools


def _get_or_create_conversation(db, conversation_id: str, user_id: int):
    try:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if not conversation:
            conversation = models.Conversation(
                id=conversation_id,
                user_id=user_id,
                title="New conversation"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        return conversation
    except Exception as e:
        db.rollback()
        print(f"[DB] Error creating conversation: {str(e)}")
        return None


def _save_message(db, conversation_id: str, role: str, content: str):
    try:
        now = datetime.now(timezone.utc)
        message = models.Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now
        )
        db.add(message)

        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        if conversation:
            if role == "user" and conversation.title == "New conversation":
                conversation.title = content[:40] + ("..." if len(content) > 40 else "")
            conversation.updated_at = now

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Error saving message: {str(e)}")


class ConversationSession:
    """Holds the orchestrator + memory manager for one conversation, cached
    for the lifetime of a single websocket connection."""

    def __init__(self, conversation_id: str, db, user_id: int):
        self.conversation_id = conversation_id
        self.memory = MemoryManager(session_id=conversation_id)
        self.orchestrator = Orchestrator(
            llm=GroqLLM(),
            tools=get_tools(user_id=user_id, db=db),
            system_prompt=system_prompt
        )

        _get_or_create_conversation(db, conversation_id, user_id)

        past_messages = db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).order_by(models.Message.created_at).all()
        self.orchestrator.history = [
            {"role": m.role, "content": m.content} for m in past_messages
        ]


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(None)):
    user_id = decode_access_token(token) if token else None
    if not user_id:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    print(f"[WebSocket] Client connected: user {user_id}")

    db = SessionLocal()
    sessions: dict[str, ConversationSession] = {}

    def get_session(conversation_id: str) -> ConversationSession:
        if conversation_id not in sessions:
            sessions[conversation_id] = ConversationSession(conversation_id, db, user_id)
        return sessions[conversation_id]

    await websocket.send_text(json.dumps({
        "type": "connected",
        "message": "Connected to Aria. How can I help you today?"
    }))

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=300
                )
            except asyncio.TimeoutError:
                continue

            payload = json.loads(data)
            message_type = payload.get("type", "message")
            conversation_id = payload.get("conversation_id")

            if not conversation_id:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "No conversation specified."
                }))
                continue

            session = get_session(conversation_id)

            if message_type == "context":
                filename = payload.get("filename", "file")
                content = payload.get("content", "")
                file_type = payload.get("file_type", "document")

                if file_type == "document":
                    context_message = f"The user uploaded a document called '{filename}'. Here is its content:\n\n{content}\n\nAcknowledge you have received it and are ready for questions."
                else:
                    context_message = f"The user uploaded an image called '{filename}'. Note: you cannot view images directly. Let the user know and ask them to describe what they need help with."

                session.memory.save_message("user", context_message)
                _save_message(db, conversation_id, "user", context_message)

                await websocket.send_text(json.dumps({
                    "type": "thinking",
                    "conversation_id": conversation_id,
                    "message": "Aria is thinking..."
                }))

                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        session.orchestrator.chat,
                        context_message
                    )
                    session.memory.save_message("assistant", response)
                    _save_message(db, conversation_id, "assistant", response)
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "conversation_id": conversation_id,
                        "message": response
                    }))
                except Exception:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "conversation_id": conversation_id,
                        "message": "Something went wrong processing your file."
                    }))
                continue

            user_message = payload.get("message", "")
            if not user_message:
                continue

            print(f"[WebSocket] Message on {conversation_id}: {user_message}")
            session.memory.save_message("user", user_message)
            _save_message(db, conversation_id, "user", user_message)

            await websocket.send_text(json.dumps({
                "type": "thinking",
                "conversation_id": conversation_id,
                "message": "Aria is thinking..."
            }))

            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    session.orchestrator.chat,
                    user_message
                )
                session.memory.save_message("assistant", response)
                _save_message(db, conversation_id, "assistant", response)
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "conversation_id": conversation_id,
                    "message": response
                }))

            except Exception as e:
                print(f"[WebSocket] Error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "conversation_id": conversation_id,
                    "message": "Something went wrong. Please try again."
                }))

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: user {user_id}")
        for session in sessions.values():
            session.memory.clear_session()
        db.close()


def _websocket_confirm(message: str) -> bool:
    print(f"[HITL] Auto-approving: {message}")
    return True