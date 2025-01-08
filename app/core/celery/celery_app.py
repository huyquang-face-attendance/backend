from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "face_attendance",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.core.celery.tasks']
)

# Optional configurations
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
