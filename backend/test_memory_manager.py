from dotenv import load_dotenv
load_dotenv()

import time
from app.memory.memory_manager import MemoryManager

manager = MemoryManager(session_id="test_session_001")
manager.clear_session()

print("=== Test 1: Save messages to short term memory ===")
manager.save_message("user", "Can you check my emails?")
manager.save_message("assistant", "Sure, here are your latest emails.")
manager.save_message("user", "I prefer to have all meetings before 10am")
manager.save_message("assistant", "Got it, I will schedule meetings before 10am.")
manager.save_message("user", "My manager is called Sarah")
print("Messages saved.")

print("\n=== Test 2: Get short term history ===")
history = manager.get_history()
for msg in history:
    print(f"  [{msg['role']}]: {msg['content']}")

print("\n=== Test 3: Recall from long term memory ===")
print("Waiting 5 seconds for Pinecone to index...")
time.sleep(5)

context = manager.recall("what time does the user prefer for meetings?")
print("Recalled context:")
print(context if context else "  Nothing found above confidence threshold.")

context = manager.recall("who is the user's manager?")
print("Recalled context:")
print(context if context else "  Nothing found above confidence threshold.")

print("\n=== Test 4: Manual long term save ===")
manager.save_to_long_term(
    text="User works on a fintech product with a team of 8 engineers",
    metadata={"type": "profile"}
)
print("Manually saved to long term memory.")

print("\n=== Test 5: Clear session ===")
manager.clear_session()
print("History count after clear:", manager.short_term.message_count())