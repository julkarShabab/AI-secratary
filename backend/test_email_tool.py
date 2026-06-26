from dotenv import load_dotenv
load_dotenv()

from app.tools.email_tool import EmailTool

tool = EmailTool()

print("=== Test 1: List emails ===")
result = tool.run({"action": "list", "max_results": 5})
if result["success"]:
    for email in result["result"]:
        print(f"  From: {email['from']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Date: {email['date']}")
        print(f"  Snippet: {email['snippet'][:80]}...")
        print()
else:
    print("Error:", result["error"])

print("=== Test 2: Read first email ===")
if result["success"] and result["result"]:
    first_id = result["result"][0]["id"]
    read_result = tool.run({"action": "read", "email_id": first_id})
    if read_result["success"]:
        email = read_result["result"]
        print(f"  From: {email['from']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Body preview: {email['body'][:200]}")
    else:
        print("Error:", read_result["error"])