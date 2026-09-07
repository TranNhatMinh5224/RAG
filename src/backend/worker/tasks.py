import asyncio
from core.celery_app import celery_app
from core.database import AsyncSessionLocal
from models import Document, User, Conversation
from services.vector_store import VectorStoreManager
from sqlalchemy import select
from core.logger import get_logger, set_request_id, set_user_id

logger = get_logger("worker.tasks")


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from core.config import settings

async def _process_ingestion(file_path: str, user_id: int, document_id: int, request_id: str | None = None):
    set_request_id(request_id)
    set_user_id(user_id)
    logger.info(f"Bắt đầu xử lý nạp tài liệu document_id={document_id} (file: {file_path})")

    task_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    task_session = async_sessionmaker(bind=task_engine, class_=AsyncSession, expire_on_commit=False)

    original_filename = None
    async with task_session() as session:
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        doc = result.scalar_one_or_none()
        if doc:
            original_filename = doc.filename

    vsm = VectorStoreManager()
    try:
        # Chạy logic Ingestion nặng (OCR, Chunking, Nhúng Vector)
        await vsm.ingest_document_async(file_path, user_id=user_id, document_id=document_id, original_filename=original_filename)
        
        # Thành công: Cập nhật DB status thành READY
        async with task_session() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "READY"
                doc.error_message = None
                await session.commit()
        logger.info(f"Hoàn tất nạp tài liệu thành công: document_id={document_id}")
    except Exception as e:
        logger.exception(f"Lỗi khi xử lý nạp tài liệu document_id={document_id}: {e}")
        # Thất bại: Cập nhật DB status thành FAILED
        async with task_session() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "FAILED"
                doc.error_message = str(e)
                await session.commit()
        raise e
    finally:
        await task_engine.dispose()
        set_request_id(None)
        set_user_id(None)


@celery_app.task(bind=True, max_retries=3)
def ingest_document_task(self, file_path: str, user_id: int, document_id: int, request_id: str | None = None):
    """
    Task xử lý ngầm (Background Task) có bảo toàn Distributed Request-ID.
    """
    asyncio.run(_process_ingestion(file_path, user_id, document_id, request_id=request_id))
