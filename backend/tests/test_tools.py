import pytest
from app.tools.base_tool import BaseTool
from app.tools.search_tool import SearchTool
from typing import Dict, Any
from unittest.mock import patch, MagicMock


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool"

    @property
    def parameters(self) -> Dict:
        return {
            "message": {
                "type": "string",
                "description": "A test message",
                "required": True
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        return {
            "success": True,
            "result": f"Received: {params['message']}",
            "error": None
        }


# ===== Base Tool Tests =====

def test_base_tool_valid_params():
    tool = DummyTool()
    result = tool.run({"message": "hello"})
    assert result["success"] is True
    assert "Received: hello" in result["result"]

def test_base_tool_missing_required_param():
    tool = DummyTool()
    result = tool.run({})
    assert result["success"] is False
    assert "Missing required parameter" in result["error"]

def test_base_tool_name():
    tool = DummyTool()
    assert tool.name == "dummy_tool"

def test_base_tool_description():
    tool = DummyTool()
    assert tool.description == "A dummy tool"

def test_base_tool_unexpected_error():
    class BrokenTool(BaseTool):
        @property
        def name(self): return "broken_tool"
        @property
        def description(self): return "Broken"
        @property
        def parameters(self): return {}
        def execute(self, params):
            raise RuntimeError("Something broke")

    tool = BrokenTool()
    result = tool.run({})
    assert result["success"] is False
    assert "Unexpected error" in result["error"]


# ===== Search Tool Tests =====

def test_search_tool_missing_query():
    tool = SearchTool()
    result = tool.run({})
    assert result["success"] is False

def test_search_tool_valid_query():
    tool = SearchTool()
    with patch.object(tool, '_search', return_value=[
        {"title": "Test Result", "url": "https://example.com", "snippet": "Test snippet"}
    ]):
        result = tool.run({"query": "test query", "max_results": 1})
        assert result["success"] is True
        assert len(result["result"]) == 1
        assert result["result"][0]["title"] == "Test Result"