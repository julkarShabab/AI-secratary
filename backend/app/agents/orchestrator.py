import json
from typing import List, Dict, Any
from app.llm.base_llm import BaseLLM
from app.tools.base_tool import BaseTool

class Orchestrator:

    def __init__(self, llm: BaseLLM, tools: List[BaseTool], system_prompt: str):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt
        self.history: List[Dict] = []

    def _build_tools_description(self) -> str:
        """
        Builds a plain text description of all available tools.
        This gets injected into the system prompt so the LLM
        knows what tools it can call and how to call them.
        """
        if not self.tools:
            return "No tools available."

        desc = "AVAILABLE TOOLS\n"
        desc += "To use a tool, respond with a JSON block like this:\n"
        desc += '```tool\n{"tool": "tool_name", "params": {"key": "value"}}\n```\n\n'
        desc += "Tools:\n"

        for tool in self.tools.values():
            desc += f"\n- {tool.name}: {tool.description}\n"
            desc += f"  Parameters: {json.dumps(tool.parameters, indent=2)}\n"

        return desc

    def _build_full_system_prompt(self) -> str:
        """
        Combines the base system prompt with tool descriptions.
        """
        tools_desc = self._build_tools_description()
        return f"{self.system_prompt}\n\n{tools_desc}"

    def _parse_tool_call(self, response: str):
        import re
        pattern = r"```(?:tool|\w+)\s*\n?\s*(\{.*?\})\s*```"
        match = re.search(pattern, response, re.DOTALL)

        if not match:
            return None, None

        try:
            json_str = match.group(1).strip()
            data = json.loads(json_str)
            tool_name = data.get("tool")
            params = data.get("params", {})
            if tool_name:
                return tool_name, params
            return None, None
        except json.JSONDecodeError:
            return None, None

    def _execute_tool(self, tool_name: str, params: Dict) -> str:
        """
        Looks up the tool by name and runs it.
        Returns the result as a string to feed back to the LLM.
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."

        tool = self.tools[tool_name]
        result = tool.run(params)

        if result["success"]:
            return f"Tool '{tool_name}' result: {json.dumps(result['result'])}"
        else:
            return f"Tool '{tool_name}' failed: {result['error']}"

    def chat(self, user_message: str) -> str:
        """
        Main method — takes a user message, runs the agentic loop,
        and returns the final response.

        The loop:
        1. Build messages with history
        2. Call LLM
        3. Check if LLM wants to use a tool
        4. If yes — execute tool, feed result back to LLM, repeat
        5. If no — return final response to user
        """
        full_system_prompt = self._build_full_system_prompt()

        self.history.append({"role": "user", "content": user_message})

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            messages = self.llm.build_messages(
                system_prompt=full_system_prompt,
                history=self.history[:-1],
                user_message=self.history[-1]["content"]
            )

            response = self.llm.chat(messages)

            tool_name, params = self._parse_tool_call(response)

            if tool_name:
                print(f"[Orchestrator] Tool call detected: {tool_name} with params {params}")

                tool_result = self._execute_tool(tool_name, params)

                print(f"[Orchestrator] Tool result: {tool_result}")

                self.history.append({"role": "assistant", "content": response})
                self.history.append({"role": "user", "content": f"[TOOL RESULT] {tool_result}"})

            else:
                self.history.append({"role": "assistant", "content": response})
                return response

        return "I was unable to complete the task after several attempts. Please try again."

    def clear_history(self):
        """
        Clears conversation history.
        Call this to start a fresh conversation.
        """
        self.history = []