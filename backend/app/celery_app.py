from celery import Celery
from app.config import Config

celery_app = Celery(
    "worker",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.report_tasks",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure periodic tasks (beat schedule)
celery_app.conf.beat_schedule = {
    "cleanup-old-logs-daily": {
        "task": "app.tasks.notification_tasks.cleanup_old_logs",
        "schedule": 86400.0,  # Every 24 hours
    },
    "generate-daily-reports": {
        "task": "app.tasks.report_tasks.generate_daily_report",
        "schedule": 86400.0,  # Every 24 hours at midnight
    },
}
