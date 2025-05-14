# app/celery_worker.py
from celery.signals import worker_ready
from celery_app import celery_app  # make sure celery.py defines `celery_app`

@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    print("Celery worker is ready!")

if __name__ == '__main__':
    celery_app.start()
