import pytest
from unittest.mock import MagicMock, patch
from app.agents.orchestrator import Orchestrator
from app.agents.tool_router import ToolRouter
from app.agents.hitl_gate import HitlGate
from app.tools.base_tool import BaseTool
from typing import Dict, Any


class MockTool(BaseTool):
    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "A mock tool for testing"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "description": "The action to perform",
                "required": True
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        return {
            "success": True,
            "result": f"Mock result for action: {params.get('action')}",
            "error": None
        }


class MockLLM:
    def chat(self, messages):
        return "Hello! I am Aria, your AI personal secretary."

    def stream(self, messages):
        yield "Hello!"

    def build_messages(self, system_prompt, history, user_message):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages


# ===== Tool Router Tests =====

def test_tool_router_registers_tools():
    router = ToolRouter([MockTool()])
    assert router.has_tool("mock_tool")
    assert not router.has_tool("nonexistent_tool")

def test_tool_router_executes_valid_tool():
    router = ToolRouter([MockTool()])
    result = router.execute("mock_tool", {"action": "test"})
    assert result["success"] is True
    assert "Mock result" in result["result"]

def test_tool_router_handles_missing_tool():
    router = ToolRouter([MockTool()])
    result = router.execute("nonexistent_tool", {})
    assert result["success"] is False
    assert "not found" in result["error"]

def test_tool_router_handles_missing_params():
    router = ToolRouter([MockTool()])
    result = router.execute("mock_tool", {})
    assert result["success"] is False
    assert "Missing required parameter" in result["error"]

def test_tool_router_list_tools():
    router = ToolRouter([MockTool()])
    tools = router.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "mock_tool"


# ===== HITL Gate Tests =====

def test_hitl_gate_requires_confirmation_for_send_email():
    gate = HitlGate(confirm_callback=lambda msg: True)
    assert gate.requires_confirmation("email_tool", "send_email") is True

def test_hitl_gate_no_confirmation_for_list_emails():
    gate = HitlGate(confirm_callback=lambda msg: True)
    assert gate.requires_confirmation("email_tool", "list") is False

def test_hitl_gate_approve():
    gate = HitlGate(confirm_callback=lambda msg: True)
    result = gate.confirm("email_tool", "send_email", {
        "to": "test@example.com",
        "subject": "Test"
    })
    assert result is True

def test_hitl_gate_reject():
    gate = HitlGate(confirm_callback=lambda msg: False)
    result = gate.confirm("email_tool", "send_email", {
        "to": "test@example.com",
        "subject": "Test"
    })
    assert result is False

def test_hitl_gate_requires_confirmation_for_create_event():
    gate = HitlGate(confirm_callback=lambda msg: True)
    assert gate.requires_confirmation("calendar_tool", "create_event") is True

def test_hitl_gate_requires_confirmation_for_post_slack():
    gate = HitlGate(confirm_callback=lambda msg: True)
    assert gate.requires_confirmation("slack_tool", "post_slack_message") is True


# ===== Orchestrator Tests =====

def test_orchestrator_normal_response():
    llm = MockLLM()
    orchestrator = Orchestrator(
        llm=llm,
        tools=[MockTool()],
        system_prompt="You are Aria."
    )
    response = orchestrator.chat("Hello")
    assert isinstance(response, str)
    assert len(response) > 0

def test_orchestrator_clear_history():
    llm = MockLLM()
    orchestrator = Orchestrator(
        llm=llm,
        tools=[MockTool()],
        system_prompt="You are Aria."
    )
    orchestrator.chat("Hello")
    assert len(orchestrator.history) > 0
    orchestrator.clear_history()
    assert len(orchestrator.history) == 0

def test_orchestrator_tool_call_parsing():
    llm = MockLLM()
    orchestrator = Orchestrator(
        llm=llm,
        tools=[MockTool()],
        system_prompt="You are Aria."
    )
    response_with_tool = '```tool\n{"tool": "mock_tool", "params": {"action": "test"}}\n```'
    tool_name, params = orchestrator._parse_tool_call(response_with_tool)
    assert tool_name == "mock_tool"
    assert params["action"] == "test"

def test_orchestrator_no_tool_call():
    llm = MockLLM()
    orchestrator = Orchestrator(
        llm=llm,
        tools=[MockTool()],
        system_prompt="You are Aria."
    )
    response_without_tool = "Hello! How can I help you today?"
    tool_name, params = orchestrator._parse_tool_call(response_without_tool)
    assert tool_name is None
    assert params is None