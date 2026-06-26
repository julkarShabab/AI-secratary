from dotenv import load_dotenv
load_dotenv()

print("=== Test 1: Email watcher ===")
from app.tasks.email_watcher import watch_emails
result = watch_emails()
print("Result:", result)

print("\n=== Test 2: Reminders ===")
from app.tasks.reminders import send_reminders
result = send_reminders()
print("Result:", result)

print("\n=== Test 3: Daily briefing ===")
from app.tasks.briefing import generate_daily_briefing
result = generate_daily_briefing()
print("Briefing:", result.get("briefing", "Failed"))
