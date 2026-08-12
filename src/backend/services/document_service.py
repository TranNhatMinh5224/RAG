import os
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from models.document import Document
from models.user import User
from services.vector_store import VectorStoreManager
from repositories.document_repository import DocumentRepository
from services.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    UploadTooLargeError,
    UnsupportedFileTypeError,
)

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, vsm: VectorStoreManager):
        self.doc_repo = doc_repo
        self.vsm = vsm

    async def process_upload_document(self, current_user: User, file: UploadFile) -> Document:
        """Xử lý logic upload: lưu file, ghi DB, và đưa vào Qdrant"""
        valid_extensions = ('.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg')
        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()
        if extension not in valid_extensions:
            raise UnsupportedFileTypeError(valid_extensions)

        upload_dir = Path(os.getenv("UPLOAD_DIR", "/app/data")).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / f"{current_user.id}_{uuid4().hex}{extension}"
        max_bytes = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25")) * 1024 * 1024
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
            # Gọi Repository lưu DB
            new_doc = await self.doc_repo.add(new_doc)
            
            # Đưa vào Qdrant
            await self.vsm.ingest_document_async(file_path, user_id=current_user.id, document_id=new_doc.id)
            
            return new_doc
        except Exception as e:
            file_path.unlink(missing_ok=True)
            if new_doc is not None and new_doc.id is not None:
                await self.doc_repo.delete(new_doc)
            if isinstance(e, (UnsupportedFileTypeError, UploadTooLargeError)):
                raise
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
            self.vsm.delete_document(document_id=doc.id)
        except Exception as e:
            print(f"Lỗi xóa Qdrant: {e}")
            
        await self.doc_repo.delete(doc)

    async def delete_document_logic(self, current_user: User, document_id: int) -> bool:
        try:
            await self.delete_document(current_user, document_id)
            return True
        except DocumentNotFoundError:
            return False
