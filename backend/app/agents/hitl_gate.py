from typing import Dict, Any, Callable


ACTIONS_REQUIRING_CONFIRMATION = [
    "send_email",
    "create_event",
    "update_event",
    "delete_event",
    "create_task",
    "update_task",
    "delete_task",
    "post_slack_message",
]


class HitlGate:

    def __init__(self, confirm_callback: Callable[[str], bool] = None):
        """
        confirm_callback is the function that actually asks the user.
        In terminal mode it uses input().
        In the web app it will use a WebSocket message to the frontend.
        If no callback is provided it defaults to terminal confirmation.
        """
        self.confirm_callback = confirm_callback or self._terminal_confirm

    def _terminal_confirm(self, message: str) -> bool:
        """
        Default confirmation for terminal/testing.
        Asks the user to type yes or no.
        """
        print(f"\n[HITL] Confirmation required: {message}")
        answer = input("[HITL] Approve? (yes/no): ").strip().lower()
        return answer in ["yes", "y"]

    def requires_confirmation(self, tool_name: str, action: str) -> bool:
        """
        Checks if a specific tool action needs user confirmation.
        Example: email_tool + send_email = True
                 email_tool + list = False
        """
        return action in ACTIONS_REQUIRING_CONFIRMATION

    def confirm(self, tool_name: str, action: str, params: Dict) -> bool:
        """
        Builds a human readable summary of the action and asks for confirmation.
        Returns True if approved, False if rejected.
        """
        summary = self._build_summary(tool_name, action, params)
        return self.confirm_callback(summary)

    def _build_summary(self, tool_name: str, action: str, params: Dict) -> str:
        """
        Builds a plain English summary of what the agent is about to do.
        """
        if tool_name == "email_tool" and action == "send_email":
            to = params.get("to", "unknown recipient")
            subject = params.get("subject", "no subject")
            return f"Send email to '{to}' with subject '{subject}'"

        if tool_name == "calendar_tool" and action == "create_event":
            title = params.get("title", "untitled event")
            time = params.get("time", "unknown time")
            return f"Create calendar event '{title}' at {time}"

        if tool_name == "calendar_tool" and action == "delete_event":
            title = params.get("title", "untitled event")
            return f"Delete calendar event '{title}'"

        if tool_name == "calendar_tool" and action == "update_event":
            title = params.get("title", "untitled event")
            return f"Update calendar event '{title}'"

        if tool_name == "slack_tool" and action == "post_slack_message":
            channel = params.get("channel", "unknown channel")
            return f"Post a Slack message to #{channel}"

        if tool_name == "task_tool" and action == "create_task":
            title = params.get("title", "untitled task")
            return f"Create task '{title}'"

        if tool_name == "task_tool" and action == "delete_task":
            title = params.get("title", "untitled task")
            return f"Delete task '{title}'"

        return f"Perform action '{action}' using '{tool_name}' with params: {params}"