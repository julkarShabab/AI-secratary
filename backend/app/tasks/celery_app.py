import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

celery_app = Celery(
    "ai_secretary",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379"),
    include=[
        "app.tasks.email_watcher",
        "app.tasks.reminders",
        "app.tasks.briefing"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Dhaka",
    enable_utc=True,
    beat_schedule={
        "watch-emails-every-10-minutes": {
            "task": "app.tasks.email_watcher.watch_emails",
            "schedule": 600.0,
        },
        "daily-briefing-8am": {
            "task": "app.tasks.briefing.generate_daily_briefing",
            "schedule": 86400.0,
        },
    }
)