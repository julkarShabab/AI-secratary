import json
import asyncio
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.llm.groq_llm import GroqLLM
from app.agents.orchestrator import Orchestrator
from app.agents.hitl_gate import HitlGate
from app.memory.memory_manager import MemoryManager
from app.tools.email_tool import EmailTool
from app.tools.calendar_tool import CalendarTool
from app.tools.search_tool import SearchTool
from app.tools.slack_tool import SlackTool
from app.tools.task_tool import TaskTool
from app.db.session import SessionLocal
from app.db import models
from datetime import datetime, timezone

router = APIRouter()

with open("app/prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()


def get_tools():
    return [
        EmailTool(),
        CalendarTool(),
        SearchTool(),
        SlackTool(),
        TaskTool()
    ]


def _get_or_create_conversation(db, conversation_id: str):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if not conversation:
        conversation = models.Conversation(id=conversation_id, user_id=1)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return conversation


def _save_message(db, conversation_id: str, role: str, content: str):
    now = datetime.now(timezone.utc)

    message = models.Message(conversation_id=conversation_id, role=role, content=content, created_at=now)
    db.add(message)

    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    if conversation:
        if role == "user" and conversation.title == "New conversation":
            conversation.title = content[:40] + ("..." if len(content) > 40 else "")
        conversation.updated_at = now

    db.commit()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"[WebSocket] Client connected: {session_id}")

    db = SessionLocal()
    conversation = _get_or_create_conversation(db, session_id)

    llm = GroqLLM()
    tools = get_tools()
    memory = MemoryManager(session_id=session_id)
    orchestrator = Orchestrator(
        llm=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    # Preload prior messages so Aria remembers this conversation on reconnect
    past_messages = db.query(models.Message).filter(
        models.Message.conversation_id == session_id
    ).order_by(models.Message.created_at).all()
    orchestrator.history = [{"role": m.role, "content": m.content} for m in past_messages]

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

            if message_type == "context":
                filename = payload.get("filename", "file")
                content = payload.get("content", "")
                file_type = payload.get("file_type", "document")

                if file_type == "document":
                    context_message = f"The user uploaded a document called '{filename}'. Here is its content:\n\n{content}\n\nAcknowledge you have received it and are ready for questions."
                else:
                    context_message = f"The user uploaded an image called '{filename}'. Note: you cannot view images directly. Let the user know and ask them to describe what they need help with."

                memory.save_message("user", context_message)
                _save_message(db, session_id, "user", context_message)

                await websocket.send_text(json.dumps({
                    "type": "thinking",
                    "message": "Aria is thinking..."
                }))

                try:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        orchestrator.chat,
                        context_message
                    )
                    memory.save_message("assistant", response)
                    _save_message(db, session_id, "assistant", response)
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "message": response
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Something went wrong processing your file."
                    }))
                continue

            user_message = payload.get("message", "")
            if not user_message:
                continue

            print(f"[WebSocket] Message from {session_id}: {user_message}")
            memory.save_message("user", user_message)
            _save_message(db, session_id, "user", user_message)

            await websocket.send_text(json.dumps({
                "type": "thinking",
                "message": "Aria is thinking..."
            }))

            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    orchestrator.chat,
                    user_message
                )
                memory.save_message("assistant", response)
                _save_message(db, session_id, "assistant", response)
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "message": response
                }))

            except Exception as e:
                print(f"[WebSocket] Error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Something went wrong. Please try again."
                }))

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: {session_id}")
        memory.clear_session()
        db.close()


def _websocket_confirm(message: str) -> bool:
    print(f"[HITL] Auto-approving: {message}")
    return True