from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name for the tool.
        This is what the LLM will use to call it.
        Example: "email_tool", "calendar_tool"
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Plain English description of what the tool does.
        The LLM reads this to decide which tool to use.
        Example: "Use this to read, draft, and send emails via Gmail"
        """
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """
        JSON schema describing the parameters this tool accepts.
        The LLM uses this to know what arguments to pass.
        Example:
        {
            "action": {
                "type": "string",
                "enum": ["read", "draft", "send"],
                "description": "The email action to perform"
            },
            "to": {
                "type": "string",
                "description": "Recipient email address"
            }
        }
        """
        pass

    @abstractmethod
    def execute(self, params: Dict) -> Dict[str, Any]:
        """
        Actually runs the tool with the given parameters.
        Always returns a dict with at least:
        {
            "success": True or False,
            "result": the output data,
            "error": error message if success is False
        }
        """
        pass

    def validate(self, params: Dict) -> bool:
        """
        Checks that all required parameters are present before execute() is called.
        tool_router.py calls this before every tool execution.
        """
        required = [
            key for key, val in self.parameters.items()
            if val.get("required", False)
        ]
        for key in required:
            if key not in params:
                raise ValueError(f"Missing required parameter '{key}' for tool '{self.name}'")
        return True

    def run(self, params: Dict) -> Dict[str, Any]:
        """
        Main entry point called by tool_router.py.
        Validates params first then executes.
        Never call execute() directly — always call run().
        """
        try:
            self.validate(params)
            return self.execute(params)
        except ValueError as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Unexpected error in tool '{self.name}': {str(e)}"
            }