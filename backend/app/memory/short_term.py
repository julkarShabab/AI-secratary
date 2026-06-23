import json
import redis
import os
from typing import List, Dict


class ShortTermMemory:

    def __init__(self, session_id: str):
        """
        Each user/session gets their own memory space in Redis.
        session_id is usually the user's ID or a unique session token.
        """
        self.session_id = session_id
        self.key = f"session:{session_id}:history"
        self.max_messages = 20
        self.ttl = 60 * 60 * 24  # 24 hours in seconds

        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )

    def add_message(self, role: str, content: str):
        """
        Adds a single message to the session history.
        Trims to max_messages to avoid memory bloat.
        role is either 'user' or 'assistant'.
        """
        message = json.dumps({"role": role, "content": content})
        self.client.rpush(self.key, message)
        self.client.ltrim(self.key, -self.max_messages, -1)
        self.client.expire(self.key, self.ttl)

    def get_history(self) -> List[Dict]:
        """
        Returns the full conversation history for this session
        as a list of {role, content} dicts.
        """
        messages = self.client.lrange(self.key, 0, -1)
        return [json.loads(msg) for msg in messages]

    def clear(self):
        """
        Wipes the session history from Redis.
        Call this when the user starts a fresh conversation.
        """
        self.client.delete(self.key)

    def message_count(self) -> int:
        """
        Returns how many messages are stored for this session.
        """
        return self.client.llen(self.key)