from typing import Dict, List, Any
from app.tools.base_tool import BaseTool


class ToolRouter:

    def __init__(self, tools: List[BaseTool]):
        """
        Takes a list of tools and maps them by name for fast lookup.
        """
        self.tools: Dict[str, BaseTool] = {tool.name: tool for tool in tools}

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Returns a tool by name.
        Raises an error if the tool doesn't exist.
        """
        if tool_name not in self.tools:
            available = list(self.tools.keys())
            raise ValueError(
                f"Tool '{tool_name}' not found. Available tools: {available}"
            )
        return self.tools[tool_name]

    def execute(self, tool_name: str, params: Dict) -> Dict[str, Any]:
        """
        Looks up the tool by name, validates params, and executes it.
        Always returns a consistent dict with success, result, error.
        """
        try:
            tool = self.get_tool(tool_name)
            return tool.run(params)
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
                "error": f"Unexpected error while routing to '{tool_name}': {str(e)}"
            }

    def list_tools(self) -> List[Dict]:
        """
        Returns a summary of all registered tools.
        Used by the orchestrator to build the tools description for the LLM.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]

    def has_tool(self, tool_name: str) -> bool:
        """
        Quick check if a tool exists without raising an error.
        """
        return tool_name in self.tools