from abc import ABC, abstractmethod
from typing import List, Dict, Generator

class BaseLLM(ABC):

    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        """
        Send a list of messages and get a full response back.
        
        messages format:
        [
            {"role": "system", "content": "You are an AI secretary..."},
            {"role": "user", "content": "Summarize my emails"},
            {"role": "assistant", "content": "Sure, here are your emails..."},
        ]
        """
        pass

    @abstractmethod
    def stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        Same as chat() but streams the response token by token.
        Used for the chat UI so the user sees words appearing live.
        """
        pass

    def build_messages(self, system_prompt: str, history: List[Dict], user_message: str) -> List[Dict]:
        """
        Helper to assemble the messages list from parts.
        Every LLM call in the project goes through this.
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        return messages