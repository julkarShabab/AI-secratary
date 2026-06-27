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


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"[WebSocket] Client connected: {session_id}")

    llm = GroqLLM()
    tools = get_tools()
    memory = MemoryManager(session_id=session_id)
    orchestrator = Orchestrator(
        llm=llm,
        tools=tools,
        system_prompt=system_prompt
    )

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
            user_message = payload.get("message", "")

            if not user_message:
                continue

            print(f"[WebSocket] Message from {session_id}: {user_message}")
            memory.save_message("user", user_message)

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


def _websocket_confirm(message: str) -> bool:
    print(f"[HITL] Auto-approving: {message}")
    return True