from dotenv import load_dotenv
load_dotenv()

from app.tools.task_tool import TaskTool

tool = TaskTool()

print("=== Test 1: List tasks ===")
result = tool.run({"action": "list", "max_results": 5})
if result["success"]:
    if result["result"]:
        for task in result["result"]:
            print(f"  [{task['id']}] {task['title']}")
            print(f"  Status: {task['status']} | Priority: {task['priority']}")
            print()
    else:
        print("  No tasks found.")
else:
    print("Error:", result["error"])

print("=== Test 2: Create a task ===")
result = tool.run({
    "action": "create",
    "title": "Test task created by Aria",
    "description": "This is a test task created by the AI Secretary",
    "priority": "Medium"
})
if result["success"]:
    print("  Task created!")
    print("  ID:", result["result"]["id"])
    print("  URL:", result["result"]["url"])
else:
    print("Error:", result["error"])

print("\n=== Test 3: Get task details ===")
if result["success"]:
    issue_key = result["result"]["id"]
    get_result = tool.run({"action": "get", "issue_key": issue_key})
    if get_result["success"]:
        task = get_result["result"]
        print(f"  Title: {task['title']}")
        print(f"  Status: {task['status']}")
        print(f"  Priority: {task['priority']}")
    else:
        print("Error:", get_result["error"])

print("\n=== Test 4: Missing param ===")
result = tool.run({"action": "create"})
print("Result:", result)