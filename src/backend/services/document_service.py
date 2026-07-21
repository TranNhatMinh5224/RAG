import os
from fastapi import UploadFile, HTTPException
from models.document import Document
from models.user import User
from services.vector_store import VectorStoreManager
from repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository, vsm: VectorStoreManager):
        self.doc_repo = doc_repo
        self.vsm = vsm

    async def process_upload_document(self, current_user: User, file: UploadFile) -> Document:
        """Xử lý logic upload: lưu file, ghi DB, và đưa vào Qdrant"""
        valid_extensions = ('.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg')
        if not file.filename.lower().endswith(valid_extensions):
            raise HTTPException(status_code=400, detail=f"Hệ thống hiện chỉ hỗ trợ các định dạng: {', '.join(valid_extensions)}")
        
        os.makedirs("/app/data", exist_ok=True)
        file_path = f"/app/data/{current_user.id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        try:
            new_doc = Document(user_id=current_user.id, filename=file.filename, file_path=file_path)
            # Gọi Repository lưu DB
            new_doc = await self.doc_repo.add(new_doc)
            
            # Đưa vào Qdrant
            await self.vsm.ingest_document_async(file_path, user_id=current_user.id, document_id=new_doc.id)
            
            return new_doc
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")

    async def get_user_documents(self, current_user: User) -> list[Document]:
        return await self.doc_repo.get_by_user_id(current_user.id)

    async def delete_document_logic(self, current_user: User, document_id: int) -> bool:
        doc = await self.doc_repo.get_by_id_and_user(document_id, current_user.id)
        if not doc:
            return False
        
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            
        try:
            self.vsm.delete_document(document_id=doc.id)
        except Exception as e:
            print(f"Lỗi xóa Qdrant: {e}")
            
        await self.doc_repo.delete(doc)
        return True
