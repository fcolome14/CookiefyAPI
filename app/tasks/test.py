# app/tasks/test.py
from celery import shared_task
from app.utils.logger import get_logger

logger = get_logger(__name__)

@shared_task
def say_hello():
    logger.info("👋 Running 'say_hello' task")
    return "Done"
