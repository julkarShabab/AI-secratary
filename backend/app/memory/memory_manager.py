import os
from typing import List, Dict, Any, Optional
from app.memory.short_term import ShortTermMemory

ENABLE_LONG_TERM_MEMORY = os.getenv("ENABLE_LONG_TERM_MEMORY", "true").lower() == "true"


SAVE_TO_LONG_TERM_KEYWORDS = [
    "my name is",
    "i prefer",
    "i like",
    "i don't like",
    "i dislike",
    "i work at",
    "my manager",
    "my boss",
    "my team",
    "my role",
    "i am a",
    "remind me",
    "always",
    "never",
    "every day",
    "every week",
]


class MemoryManager:

    def __init__(self, session_id: str):
        """
        Unified interface for both short and long term memory.
        session_id ties the short term memory to a specific user session.
        """
        self.short_term = ShortTermMemory(session_id=session_id)
        self.long_term: Optional[Any] = None
        if ENABLE_LONG_TERM_MEMORY:
            from app.memory.long_term import LongTermMemory  # heavy import (torch); only pay for it if enabled
            self.long_term = LongTermMemory()

    def save_message(self, role: str, content: str):
        """
        Saves every message to short term memory.
        Also checks if the message contains important information
        worth saving to long term memory.
        """
        self.short_term.add_message(role=role, content=content)

        if role == "user" and self.long_term and self._should_save_long_term(content):
            self.long_term.save(
                text=content,
                metadata={"type": "user_statement", "source": "conversation"}
            )
            print(f"[MemoryManager] Saved to long term memory: '{content[:60]}'")

    def get_history(self) -> List[Dict]:
        """
        Returns short term conversation history.
        This gets injected into every LLM call.
        """
        return self.short_term.get_history()

    def recall(self, query: str, top_k: int = 3) -> str:
        """
        Searches long term memory for relevant context.
        Returns a formatted string ready to inject into the system prompt.
        """
        if not self.long_term:
            return ""

        results = self.long_term.recall(query=query, top_k=top_k)

        if not results:
            return ""

        high_confidence = [r for r in results if r["score"] > 0.5]

        if not high_confidence:
            return ""

        context = "RELEVANT USER CONTEXT FROM MEMORY:\n"
        for r in high_confidence:
            context += f"- {r['text']}\n"
        return context

    def save_to_long_term(self, text: str, metadata: Dict[str, Any] = {}):
        """
        Manually save something important to long term memory.
        Call this when the orchestrator detects key user information.
        """
        if self.long_term:
            self.long_term.save(text=text, metadata=metadata)

    def clear_session(self):
        """
        Clears short term memory for this session.
        Long term memory is never cleared automatically.
        """
        self.short_term.clear()
        print(f"[MemoryManager] Session cleared.")

    def _should_save_long_term(self, text: str) -> bool:
        """
        Checks if a user message contains information worth
        remembering permanently in long term memory.
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in SAVE_TO_LONG_TERM_KEYWORDS)