from celery.signals import worker_ready
from celery_app import celery_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    logger.info("Celery worker is ready!")

if __name__ == '__main__':
    celery_app.start()
