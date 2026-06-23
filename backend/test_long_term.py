from dotenv import load_dotenv
load_dotenv()

import time
from app.memory.long_term import LongTermMemory

memory = LongTermMemory()

print("=== Test 1: Save memories ===")
memory.save("User prefers morning meetings before 10am", {"type": "preference"})
memory.save("User is a backend engineer working on Python and FastAPI", {"type": "profile"})
memory.save("User's manager is called Sarah", {"type": "contact"})
memory.save("User dislikes long emails and prefers bullet points", {"type": "preference"})
memory.save("User works at a fintech startup with a team of 8 engineers", {"type": "profile"})
print("All memories saved.")

print("\n=== Test 2: Recall by semantic query ===")
print("Waiting 5 seconds for Pinecone to index...")
time.sleep(5)

results = memory.recall("what time does the user prefer for meetings?")
print("Query: 'what time does the user prefer for meetings?'")
for r in results:
    print(f"  [{r['score']}] {r['text']}")

print()
results = memory.recall("who is the user's boss?")
print("Query: 'who is the user's boss?'")
for r in results:
    print(f"  [{r['score']}] {r['text']}")

print("\n=== Test 3: Recall email preferences ===")
results = memory.recall("how does the user like to receive information?")
print("Query: 'how does the user like to receive information?'")
for r in results:
    print(f"  [{r['score']}] {r['text']}")