from typing import Dict, Any
from app.tools.base_tool import BaseTool

class DummyTool(BaseTool):

    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool for testing base_tool.py"

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
            "result": f"Tool received: {params['message']}",
            "error": None
        }

tool = DummyTool()

print("Tool name:", tool.name)
print("Tool description:", tool.description)

# Test 1 - valid params
response = tool.run({"message": "hello from base tool test"})
print("Test 1 (valid):", response)

# Test 2 - missing required param
response = tool.run({})
print("Test 2 (missing param):", response)