from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "cookiefyapi",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_result,
)

celery_app.autodiscover_tasks(['app.tasks'])

celery_app.conf.beat_schedule = {
    "say-hello-every-30s": {
        "task": "app.tasks.test.say_hello",
        "schedule": 30.0,
    }
}

import app.tasks.test # Import the task in case it is not auto-discovered