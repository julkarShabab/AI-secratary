from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.agents.tool_router import ToolRouter


class DummyEmailTool(BaseTool):

    @property
    def name(self) -> str:
        return "email_tool"

    @property
    def description(self) -> str:
        return "Read the user's latest emails"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list"],
                "description": "The action to perform",
                "required": True
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        return {
            "success": True,
            "result": ["Email 1", "Email 2", "Email 3"],
            "error": None
        }


class DummyCalendarTool(BaseTool):

    @property
    def name(self) -> str:
        return "calendar_tool"

    @property
    def description(self) -> str:
        return "Check and manage calendar events"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list"],
                "description": "The action to perform",
                "required": True
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        return {
            "success": True,
            "result": ["Meeting at 10am", "Standup at 2pm"],
            "error": None
        }


router = ToolRouter([DummyEmailTool(), DummyCalendarTool()])

print("=== Test 1: List all tools ===")
for tool in router.list_tools():
    print(f"- {tool['name']}: {tool['description']}")

print("\n=== Test 2: Execute valid tool ===")
result = router.execute("email_tool", {"action": "list"})
print("Result:", result)

print("\n=== Test 3: Execute tool with missing params ===")
result = router.execute("email_tool", {})
print("Result:", result)

print("\n=== Test 4: Execute tool that does not exist ===")
result = router.execute("slack_tool", {"action": "list"})
print("Result:", result)

print("\n=== Test 5: has_tool check ===")
print("Has email_tool:", router.has_tool("email_tool"))
print("Has slack_tool:", router.has_tool("slack_tool"))