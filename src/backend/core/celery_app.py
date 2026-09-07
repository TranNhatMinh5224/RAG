from celery import Celery
from core.config import settings

# URL kết nối Redis (Hỗ trợ redis:// cục bộ và rediss:// TLS trên AWS ElastiCache)
REDIS_URL = settings.REDIS_URL or settings.RABBITMQ_URL

celery_app = Celery(
    "rag_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
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
