from dotenv import load_dotenv
load_dotenv()

from app.tools.slack_tool import SlackTool

tool = SlackTool()

print("=== Test 1: List channels ===")
result = tool.run({"action": "list_channels"})
if result["success"]:
    for channel in result["result"]:
        print(f"  #{channel['name']} — ID: {channel['id']} — Members: {channel['member_count']}")
else:
    print("Error:", result["error"])

print("\n=== Test 2: Read messages from first channel ===")
if result["success"] and result["result"]:
    first_channel_id = result["result"][0]["id"]
    first_channel_name = result["result"][0]["name"]
    print(f"Reading from #{first_channel_name}...")

    read_result = tool.run({
        "action": "read_messages",
        "channel_id": first_channel_id,
        "limit": 5
    })
    if read_result["success"]:
        for msg in read_result["result"]:
            print(f"  [{msg['user']}]: {msg['text'][:80]}")
    else:
        print("Error:", read_result["error"])

print("\n=== Test 3: Missing param ===")
result = tool.run({"action": "post_message"})
print("Result:", result)
