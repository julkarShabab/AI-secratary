from dotenv import load_dotenv
load_dotenv()

from app.memory.short_term import ShortTermMemory

memory = ShortTermMemory(session_id="test_user_123")

memory.clear()

print("=== Test 1: Add messages ===")
memory.add_message("user", "Can you check my emails?")
memory.add_message("assistant", "Sure, here are your latest emails...")
memory.add_message("user", "What about my calendar?")
memory.add_message("assistant", "You have a meeting at 10am tomorrow.")
print("Messages added:", memory.message_count())

print("\n=== Test 2: Get history ===")
history = memory.get_history()
for msg in history:
    print(f"  [{msg['role']}]: {msg['content']}")

print("\n=== Test 3: Max messages trim ===")
for i in range(20):
    memory.add_message("user", f"Test message {i}")
print("Message count after adding 20 more (should be 20):", memory.message_count())

print("\n=== Test 4: Clear history ===")
memory.clear()
print("Message count after clear (should be 0):", memory.message_count())