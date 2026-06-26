from dotenv import load_dotenv
load_dotenv()

from app.tools.search_tool import SearchTool

tool = SearchTool()

print("=== Test 1: General search ===")
result = tool.run({
    "query": "latest trends in AI 2026",
    "max_results": 3
})
if result["success"]:
    for r in result["result"]:
        print(f"  Title: {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  Snippet: {r['snippet'][:100]}...")
        print()
else:
    print("Error:", result["error"])

print("=== Test 2: Tech news search ===")
result = tool.run({
    "query": "Python FastAPI best practices 2026",
    "max_results": 3
})
if result["success"]:
    for r in result["result"]:
        print(f"  Title: {r['title']}")
        print(f"  URL: {r['url']}")
        print()
else:
    print("Error:", result["error"])

print("=== Test 3: Missing query param ===")
result = tool.run({})
print("Result:", result)