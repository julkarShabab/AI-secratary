from dotenv import load_dotenv
load_dotenv()

from app.llm.groq_llm import GroqLLM
from app.llm.base_llm import BaseLLM

with open("app/prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()

llm: BaseLLM = GroqLLM()

messages = llm.build_messages(
    system_prompt=system_prompt,
    history=[],
    user_message="Say hello and introduce yourself in one sentence."
)

response = llm.chat(messages)
print("Response:", response)