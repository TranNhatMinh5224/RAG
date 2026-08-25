from celery import Celery
from core.config import settings

# URL kết nối mặc định của RabbitMQ
RABBITMQ_URL = settings.RABBITMQ_URL

celery_app = Celery(
    "rag_tasks",
    broker=RABBITMQ_URL,
    include=["worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)
