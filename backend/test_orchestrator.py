from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any
from app.llm.groq_llm import GroqLLM
from app.tools.base_tool import BaseTool
from app.agents.orchestrator import Orchestrator

with open("app/prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()

# Dummy tool to simulate a real tool
class DummyEmailTool(BaseTool):

    @property
    def name(self) -> str:
        return "email_tool"

    @property
    def description(self) -> str:
        return "Use this to read the user's latest emails"

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
            "result": [
                {"from": "boss@company.com", "subject": "Q3 Review meeting tomorrow at 10am"},
                {"from": "client@startup.com", "subject": "Project proposal follow up"},
                {"from": "hr@company.com", "subject": "Leave balance reminder"}
            ],
            "error": None
        }

llm = GroqLLM()
tools = [DummyEmailTool()]

orchestrator = Orchestrator(
    llm=llm,
    tools=tools,
    system_prompt=system_prompt
)

print("=== Test 1: Normal conversation (no tool) ===")
response = orchestrator.chat("What can you help me with today?")
print("Response:", response)

orchestrator.clear_history()

print("\n=== Test 2: Tool usage ===")
response = orchestrator.chat("Can you check my latest emails?")
print("Response:", response)