import os
from typing import List, Dict, Generator
from google import genai
from app.llm.base_llm import BaseLLM

class GeminiLLM(BaseLLM):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in your .env file")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"

    def chat(self, messages: List[Dict]) -> str:
        prompt = self._convert_messages(messages)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        prompt = self._convert_messages(messages)
        for chunk in self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt
        ):
            if chunk.text:
                yield chunk.text

    def _convert_messages(self, messages: List[Dict]) -> str:
        result = ""
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            if role == "SYSTEM":
                result += f"[SYSTEM INSTRUCTIONS]\n{content}\n\n"
            elif role == "USER":
                result += f"User: {content}\n"
            elif role == "ASSISTANT":
                result += f"Assistant: {content}\n"
        return result.strip()