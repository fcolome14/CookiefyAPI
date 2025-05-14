from celery import Celery
from app.core.config import settings

celery_app = Celery(
    settings.project_name,
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_result,
)
celery_app.autodiscover_tasks(['app.tasks'])

celery_app.conf.beat_schedule = {
    "scraping-asian-restaurants-bcn": {
        "task": "app.tasks.scraper.scrap",
        "schedule": settings.beat_scheduler_seconds,
    }
}

import app.tasks.scraper # Import the task in case it is not auto-discovered