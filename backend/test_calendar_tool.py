from dotenv import load_dotenv
load_dotenv()

from app.tools.calendar_tool import CalendarTool

tool = CalendarTool()

print("=== Test 1: List upcoming events ===")
result = tool.run({"action": "list", "max_results": 5})
if result["success"]:
    if result["result"]:
        for event in result["result"]:
            print(f"  Title: {event['title']}")
            print(f"  Start: {event['start']}")
            print(f"  End: {event['end']}")
            print()
    else:
        print("  No upcoming events found.")
else:
    print("Error:", result["error"])

print("=== Test 2: Check availability ===")
result = tool.run({
    "action": "check_availability",
    "start": "2026-06-27T10:00:00+06:00",
    "end": "2026-06-27T11:00:00+06:00"
})
if result["success"]:
    availability = result["result"]
    if availability["available"]:
        print("  Time slot is available!")
    else:
        print("  Conflicts found:", availability["conflicts"])
else:
    print("Error:", result["error"])

print("\n=== Test 3: Create event (requires HITL in production) ===")
result = tool.run({
    "action": "create",
    "title": "Test Event from Aria",
    "start": "2026-06-28T10:00:00+06:00",
    "end": "2026-06-28T11:00:00+06:00",
    "description": "This is a test event created by AI Secretary"
})
if result["success"]:
    print("  Event created successfully!")
    print("  Event ID:", result["result"]["event_id"])
    print("  Link:", result["result"]["link"])
else:
    print("Error:", result["error"])