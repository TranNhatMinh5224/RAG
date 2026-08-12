from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.dependencies import get_current_user, get_document_service
from models.schemas import DocumentResponse, StatusResponse
from models.user import User
from services.document_service import DocumentService
from services.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    UploadTooLargeError,
    UnsupportedFileTypeError,
)

router = APIRouter(
    prefix="/document",
    tags=["Document Management"],
)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return await doc_service.process_upload_document(current_user, file)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(exc.valid_extensions)}",
        )
    except UploadTooLargeError:
        raise HTTPException(status_code=413, detail="Uploaded file is too large")
    except DocumentProcessingError:
        raise HTTPException(status_code=500, detail="Could not process document")


@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
):
    return await doc_service.get_user_documents(current_user)


@router.delete("/{document_id}", response_model=StatusResponse)
async def delete_document(
    document_id: int,
    doc_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    try:
        await doc_service.delete_document(current_user, document_id)
        return {"status": "success", "message": "Document deleted successfully"}
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
