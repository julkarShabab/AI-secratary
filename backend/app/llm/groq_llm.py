import os
from typing import List, Dict, Generator
from groq import Groq
from app.llm.base_llm import BaseLLM

class GroqLLM(BaseLLM):

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in your .env file")
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"

    def chat(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    def stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _convert_messages(self, messages: List[Dict]) -> str:
        return messages