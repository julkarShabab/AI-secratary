"""
In-process job scheduler.

This replaces Celery + Celery Beat. Since none of our background jobs
are triggered by user requests (they're all time-based: "run every
10 minutes", "run once a day"), we don't need a separate broker,
worker process, or beat process — APScheduler runs them on a timer
inside the same process as the FastAPI app.

This means the whole backend is a single process, which fits
comfortably on a free-tier host (Render, Railway, Fly.io, etc.)
where a paid, always-on worker service is what the Celery setup
used to require.

Trade-off vs. Celery: jobs run in-process, so a long-running job
can share resources with request handling, and jobs don't survive
a process restart mid-run (they just fire again on their next
schedule). For jobs this lightweight (a few API calls + one LLM
call), that's a non-issue.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks.email_watcher import watch_emails
from app.tasks.reminders import send_reminders
from app.tasks.briefing import generate_daily_briefing

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Dhaka")


def _run_safely(name: str, func):
    """Wrap a job so one failing job can't crash the scheduler loop."""
    try:
        func()
    except Exception as e:
        logger.error(f"[Scheduler] Job '{name}' failed: {e}")


def start_scheduler():
    """Register jobs and start the scheduler. Call once on app startup."""
    scheduler.add_job(
        lambda: _run_safely("watch_emails", watch_emails),
        trigger="interval",
        seconds=600,
        id="watch-emails-every-10-minutes",
        replace_existing=True,
    )

    scheduler.add_job(
        lambda: _run_safely("send_reminders", send_reminders),
        trigger="interval",
        seconds=600,
        id="send-reminders-every-10-minutes",
        replace_existing=True,
    )

    scheduler.add_job(
        lambda: _run_safely("generate_daily_briefing", generate_daily_briefing),
        trigger="cron",
        hour=8,
        minute=0,
        id="daily-briefing-8am",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[Scheduler] Started with jobs: %s", [job.id for job in scheduler.get_jobs()])


def stop_scheduler():
    """Call on app shutdown to clean up cleanly."""
    if scheduler.running:
        scheduler.shutdown(wait=False)