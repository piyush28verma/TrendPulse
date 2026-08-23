"""
TrendPulse — Scheduler
APScheduler-based daily trigger for the pipeline.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from backend.config import settings

scheduler = BackgroundScheduler()
_pipeline_callback = None
_last_run = None
_next_run = None


def set_pipeline_callback(callback):
    """Register the pipeline function to be called on schedule."""
    global _pipeline_callback
    _pipeline_callback = callback


def _run_scheduled():
    """Internal scheduled job runner."""
    global _last_run
    _last_run = datetime.utcnow().isoformat()
    if _pipeline_callback:
        _pipeline_callback()


def start_scheduler():
    """Start the daily scheduler."""
    global _next_run

    trigger = CronTrigger(
        hour=settings.POST_SCHEDULE_HOUR,
        minute=settings.POST_SCHEDULE_MINUTE,
    )

    scheduler.add_job(
        _run_scheduled,
        trigger=trigger,
        id="daily_trendpulse",
        replace_existing=True,
        name="TrendPulse Daily Auto-Post",
    )

    scheduler.start()

    # Calculate next run time
    job = scheduler.get_job("daily_trendpulse")
    if job and job.next_run_time:
        _next_run = job.next_run_time.isoformat()


def get_scheduler_status() -> dict:
    """Get current scheduler status."""
    job = scheduler.get_job("daily_trendpulse")
    next_run = job.next_run_time.isoformat() if job and job.next_run_time else None

    return {
        "running": scheduler.running,
        "schedule_time": f"{settings.POST_SCHEDULE_HOUR:02d}:{settings.POST_SCHEDULE_MINUTE:02d} UTC",
        "next_run": next_run,
        "last_run": _last_run,
        "job_id": "daily_trendpulse",
    }


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
