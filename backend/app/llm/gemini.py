import os
import base64
import time
from typing import List, Dict, Generator
from google import genai
from google.genai import types
from app.llm.base_llm import BaseLLM


class GeminiLLM(BaseLLM):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in your .env file")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash-latest"

    def chat(self, messages: List[Dict]) -> str:
        prompt = self._convert_messages(messages)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

    def analyze_image(self, base64_image: str, prompt: str) -> str:
        """
        Analyzes an image using Gemini vision.
        Retries up to 3 times if rate limited.
        """
        image_bytes = base64.b64decode(base64_image)

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        prompt
                    ]
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < 2:
                        print(f"[Gemini] Rate limited, waiting 30s... (attempt {attempt + 1}/3)")
                        time.sleep(30)
                        continue
                    return "Image analysis temporarily unavailable due to rate limits. Please try again in a few minutes."
                return f"Could not analyze image: {error_str}"

        return "Image analysis failed after multiple attempts."

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