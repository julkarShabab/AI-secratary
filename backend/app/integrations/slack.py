import os
from typing import List, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackIntegration:

    def __init__(self):
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            raise ValueError("SLACK_BOT_TOKEN is not set in your .env file")
        self.client = WebClient(token=token)

    def list_channels(self) -> List[Dict]:
        """
        Returns all public channels in the workspace.
        """
        try:
            result = self.client.conversations_list(types="public_channel")
            channels = result["channels"]
            return [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "member_count": c.get("num_members", 0),
                    "topic": c.get("topic", {}).get("value", "")
                }
                for c in channels
            ]
        except SlackApiError as e:
            raise Exception(f"Failed to list channels: {e.response['error']}")

    def read_messages(self, channel_id: str, limit: int = 10) -> List[Dict]:
        """
        Returns recent messages from a channel.
        """
        try:
            result = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            messages = result["messages"]
            output = []
            for msg in messages:
                output.append({
                    "user": msg.get("user", "unknown"),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("ts", "")
                })
            return output
        except SlackApiError as e:
            raise Exception(f"Failed to read messages: {e.response['error']}")

    def post_message(self, channel_id: str, message: str) -> Dict:
        """
        Posts a message to a channel.
        Always called after HITL confirmation.
        """
        try:
            result = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            return {
                "success": True,
                "timestamp": result["ts"],
                "channel": result["channel"]
            }
        except SlackApiError as e:
            raise Exception(f"Failed to post message: {e.response['error']}")

    def get_user_info(self, user_id: str) -> Dict:
        """
        Returns info about a Slack user by their ID.
        """
        try:
            result = self.client.users_info(user=user_id)
            user = result["user"]
            return {
                "id": user["id"],
                "name": user["name"],
                "real_name": user.get("real_name", ""),
                "email": user.get("profile", {}).get("email", "")
            }
        except SlackApiError as e:
            raise Exception(f"Failed to get user info: {e.response['error']}")