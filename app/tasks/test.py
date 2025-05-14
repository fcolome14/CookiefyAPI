# app/tasks/test.py
from celery import shared_task

@shared_task
def say_hello():
    print("👋 Hello from Celery!")
    return "Done"
