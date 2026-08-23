"""
TrendPulse — Scheduler
APScheduler-based daily trigger for the pipeline.
"""
import asyncio
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from backend.config import settings

scheduler = BackgroundScheduler()
_pipeline_callback = None
_last_run = None


def set_pipeline_callback(callback):
    global _pipeline_callback
    _pipeline_callback = callback


def _run_scheduled():
    global _last_run
    _last_run = datetime.utcnow().isoformat()
    if _pipeline_callback:
        try:
            # The callback is an async function; we need to run it properly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_pipeline_callback())
            finally:
                loop.close()
        except Exception as e:
            print(f"[Scheduler] Pipeline execution error: {e}")


def start_scheduler():
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


def get_scheduler_status() -> dict:
    job = scheduler.get_job("daily_trendpulse")
    next_run = None
    if job and job.next_run_time:
        next_run = job.next_run_time.isoformat()

    return {
        "running": scheduler.running,
        "schedule_time": f"{settings.POST_SCHEDULE_HOUR:02d}:{settings.POST_SCHEDULE_MINUTE:02d} UTC",
        "next_run": next_run,
        "last_run": _last_run,
        "job_id": "daily_trendpulse",
    }


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
