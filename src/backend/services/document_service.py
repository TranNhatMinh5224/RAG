import os
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from models.document import Document
from models.user import User
from services.vector_store import VectorStoreManager
from repositories.document_repository import DocumentRepository
from services.activity_service import ActivityService
from services.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    UploadTooLargeError,
    UnsupportedFileTypeError,
)
from core.config import settings
from core.logger import get_logger, get_request_id

logger = get_logger("services.document_service")


class DocumentService:
    def __init__(
        self,
        doc_repo: DocumentRepository,
        vsm: VectorStoreManager,
        activity_service: ActivityService | None = None,
    ):
        self.doc_repo = doc_repo
        self.vsm = vsm
        self.activity_service = activity_service

    async def process_upload_document(self, current_user: User, file: UploadFile) -> Document:
        """Xử lý logic upload: lưu file, ghi DB, đẩy task Redis có kèm Request-ID và ghi Audit Log"""
        valid_extensions = ('.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg')
        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()
        if extension not in valid_extensions:
            raise UnsupportedFileTypeError(valid_extensions)

        upload_dir = Path(settings.UPLOAD_DIR).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{current_user.id}_{uuid4().hex}{extension}"
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        bytes_written = 0

        try:
            with file_path.open("wb") as output:
                while chunk := await file.read(1024 * 1024):
                    bytes_written += len(chunk)
                    if bytes_written > max_bytes:
                        raise UploadTooLargeError
                    output.write(chunk)
        except Exception:
            file_path.unlink(missing_ok=True)
            raise
        
        new_doc = None
        try:
            new_doc = Document(user_id=current_user.id, filename=original_name, file_path=str(file_path))
            new_doc = await self.doc_repo.add(new_doc)
            
            # Gửi task vào Redis Queue cho Celery Worker xử lý ngầm (Non-blocking) kèm Distributed Request-ID
            req_id = get_request_id()
            from worker.tasks import ingest_document_task
            ingest_document_task.delay(str(file_path), current_user.id, new_doc.id, request_id=req_id)
            logger.info(
                f"Đã đưa tài liệu {new_doc.id} ({original_name}) vào hàng đợi xử lý",
                extra={"document_id": new_doc.id, "file_name": original_name}
            )

            # Ghi Activity Log (Audit Trail)
            if self.activity_service:
                await self.activity_service.record_activity(
                    action="DOCUMENT_UPLOAD",
                    user_id=current_user.id,
                    resource_type="document",
                    resource_id=str(new_doc.id),
                    details=f"Tải lên tài liệu: {original_name}",
                    request_id=req_id,
                )
            
            return new_doc
        except Exception as e:
            file_path.unlink(missing_ok=True)
            if new_doc is not None and new_doc.id is not None:
                await self.doc_repo.delete(new_doc)
            if isinstance(e, (UnsupportedFileTypeError, UploadTooLargeError)):
                raise
            logger.exception(f"Lỗi khi tải lên tài liệu {original_name}: {e}")
            raise DocumentProcessingError

    async def get_user_documents(self, current_user: User) -> list[Document]:
        return await self.doc_repo.get_by_user_id(current_user.id)

    async def delete_document(self, current_user: User, document_id: int) -> None:
        doc = await self.doc_repo.get_by_id_and_user(document_id, current_user.id)
        if not doc:
            raise DocumentNotFoundError
        
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            
        try:
            await self.vsm.delete_document(document_id=doc.id)
        except Exception as e:
            logger.error(f"Lỗi xóa vector trên Qdrant cho document {doc.id}: {e}")
            
        await self.doc_repo.delete(doc)
        logger.info(f"Đã xóa tài liệu {document_id} ({doc.filename})")

        # Ghi Activity Log
        if self.activity_service:
            await self.activity_service.record_activity(
                action="DOCUMENT_DELETE",
                user_id=current_user.id,
                resource_type="document",
                resource_id=str(document_id),
                details=f"Xóa tài liệu: {doc.filename}",
            )

    async def delete_document_logic(self, current_user: User, document_id: int) -> bool:
        try:
            await self.delete_document(current_user, document_id)
            return True
        except DocumentNotFoundError:
            return False

