from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.integrations.slack import SlackIntegration


class SlackTool(BaseTool):

    def __init__(self):
        self.slack = SlackIntegration()

    @property
    def name(self) -> str:
        return "slack_tool"

    @property
    def description(self) -> str:
        return "Use this to list Slack channels, read messages, or post a message to a channel"

    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["list_channels", "read_messages", "post_message"],
                "description": "The Slack action to perform",
                "required": True
            },
            "channel_id": {
                "type": "string",
                "description": "Required for read_messages and post_message.",
                "required": False
            },
            "message": {
                "type": "string",
                "description": "Required for post_message. The message text to send.",
                "required": False
            },
            "limit": {
                "type": "integer",
                "description": "For read_messages. Number of messages to return. Default 10.",
                "required": False
            }
        }

    def execute(self, params: Dict) -> Dict[str, Any]:
        action = params.get("action")

        if action == "list_channels":
            channels = self.slack.list_channels()
            return {"success": True, "result": channels, "error": None}

        elif action == "read_messages":
            channel_id = params.get("channel_id")
            if not channel_id:
                return {
                    "success": False,
                    "result": None,
                    "error": "channel_id is required for action=read_messages"
                }
            messages = self.slack.read_messages(
                channel_id=channel_id,
                limit=params.get("limit", 10)
            )
            return {"success": True, "result": messages, "error": None}

        elif action == "post_message":
            channel_id = params.get("channel_id")
            message = params.get("message")
            if not all([channel_id, message]):
                return {
                    "success": False,
                    "result": None,
                    "error": "channel_id and message are required for action=post_message"
                }
            result = self.slack.post_message(
                channel_id=channel_id,
                message=message
            )
            return {"success": True, "result": result, "error": None}

        return {
            "success": False,
            "result": None,
            "error": f"Unknown action '{action}'"
        }