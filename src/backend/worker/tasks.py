import asyncio
from core.celery_app import celery_app
from core.database import AsyncSessionLocal
from models.document import Document
from services.vector_store import VectorStoreManager
from sqlalchemy import select

async def _process_ingestion(file_path: str, user_id: int, document_id: int):
    vsm = VectorStoreManager()
    try:
        # Chạy logic Ingestion nặng (OCR, Chunking, Nhúng Vector)
        await vsm.ingest_document_async(file_path, user_id=user_id, document_id=document_id)
        
        # Thành công: Cập nhật DB status thành READY
        async with AsyncSessionLocal() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "READY"
                await session.commit()
    except Exception as e:
        # Thất bại: Cập nhật DB status thành FAILED
        async with AsyncSessionLocal() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = "FAILED"
                doc.error_message = str(e)
                await session.commit()
        raise e

@celery_app.task(bind=True, max_retries=3)
def ingest_document_task(self, file_path: str, user_id: int, document_id: int):
    """
    Task xử lý ngầm (Background Task).
    Bọc bằng asyncio.run vì hàm ingest_document_async là hàm bất đồng bộ.
    """
    asyncio.run(_process_ingestion(file_path, user_id, document_id))
