from datetime import datetime, timezone, timedelta
from app.integrations.google_calendar import GoogleCalendarIntegration


def send_reminders():
    """
    Checks calendar for events in the next 30 minutes
    and logs reminders for them.
    In production this will send a notification to the user.
    """
    try:
        calendar = GoogleCalendarIntegration()

        now = datetime.now(timezone.utc)
        in_30_minutes = now + timedelta(minutes=30)

        result = calendar.check_availability(
            start=now.isoformat(),
            end=in_30_minutes.isoformat()
        )

        if result["available"]:
            print("[Reminders] No upcoming events in the next 30 minutes.")
            return {"status": "ok", "reminders_sent": 0}

        conflicts = result["conflicts"]
        print(f"[Reminders] Upcoming events: {conflicts}")

        return {
            "status": "ok",
            "reminders_sent": len(conflicts),
            "events": conflicts
        }

    except Exception as e:
        print(f"[Reminders] Error: {str(e)}")
        return {"status": "error", "error": str(e)}