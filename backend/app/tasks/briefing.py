from app.tasks.celery_app import celery_app
from app.integrations.gmail import GmailIntegration
from app.integrations.google_calendar import GoogleCalendarIntegration
from app.llm.groq_llm import GroqLLM


@celery_app.task(name="app.tasks.briefing.generate_daily_briefing")
def generate_daily_briefing():
    """
    Runs every morning at 8am.
    Pulls emails and calendar events then generates
    an AI summary briefing for the user.
    """
    try:
        gmail = GmailIntegration()
        calendar = GoogleCalendarIntegration()
        llm = GroqLLM()

        emails = gmail.list_emails(max_results=5)
        events = calendar.list_events(max_results=5)

        email_summary = "\n".join([
            f"- From: {e['from']} | Subject: {e['subject']}"
            for e in emails
        ])

        event_summary = "\n".join([
            f"- {e['title']} at {e['start']}"
            for e in events
        ])

        prompt = f"""Generate a short professional morning briefing for a tech professional.

Latest emails:
{email_summary}

Upcoming calendar events:
{event_summary}

Keep it under 150 words. Be concise and actionable."""

        messages = llm.build_messages(
            system_prompt="You are Aria, an AI personal secretary. Generate clear and concise daily briefings.",
            history=[],
            user_message=prompt
        )

        briefing = llm.chat(messages)

        print("[Briefing] Daily briefing generated:")
        print(briefing)

        return {
            "status": "ok",
            "briefing": briefing
        }

    except Exception as e:
        print(f"[Briefing] Error: {str(e)}")
        return {"status": "error", "error": str(e)}