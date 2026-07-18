from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List

from api.dependencies import get_current_user, get_document_service
from models.user import User
from models.schemas import DocumentResponse
from services.document_service import DocumentService

router = APIRouter(
    prefix="/document",
    tags=["Document Management"]
)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user)
):
    """Upload File PDF: Router chỉ định nghĩa API, DI và trả về kết quả"""
    return await doc_service.process_upload_document(current_user, file)

@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service)
):
    """Lấy danh sách các tài liệu mà User đã tải lên"""
    return await doc_service.get_user_documents(current_user)

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    doc_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user)
):
    """Xóa tài liệu"""
    success = await doc_service.delete_document_logic(current_user, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu này (hoặc bạn không có quyền xóa)")
    return {"status": "success", "message": "Đã xóa hoàn toàn tài liệu"}
