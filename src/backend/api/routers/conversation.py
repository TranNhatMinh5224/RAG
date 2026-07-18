from fastapi import APIRouter, Depends, HTTPException
from typing import List

from api.dependencies import get_current_user, get_chat_service
from models.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse
from models.user import User
from services.chat_service import ChatService

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation Management"]
)

@router.post("/", response_model=ConversationResponse)
async def create_new_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Khởi tạo một Cuộc trò chuyện mới và liên kết nó với các file PDF đã chọn"""
    try:
        conv = await chat_service.create_conversation(current_user, request.title, request.document_ids)
        return conv
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo cuộc trò chuyện: {str(e)}")

@router.get("/list", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Lấy danh sách tất cả các cuộc trò chuyện của User hiện tại"""
    return await chat_service.get_user_conversations(current_user.id)

@router.delete("/{conversation_id}")
async def delete_conversation_api(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Xóa một cuộc trò chuyện và toàn bộ tin nhắn bên trong nó"""
    success = await chat_service.delete_conversation(current_user.id, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện này")
    return {"status": "success", "message": "Đã xóa cuộc trò chuyện"}

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_details(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Lấy chi tiết cuộc trò chuyện kèm danh sách tin nhắn và tài liệu"""
    conv = await chat_service.chat_repo.get_conversation_with_documents(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện")
    messages = await chat_service.chat_repo.get_recent_messages(conversation_id, limit=50)
    # Vì schema cần thuộc tính messages, chúng ta map vào dict
    conv_dict = {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
        "documents": conv.documents,
        "messages": messages
    }
    return conv_dict

@router.post("/{conversation_id}/documents")
async def attach_documents(
    conversation_id: int,
    document_ids: list[int],
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Đính kèm tài liệu mới vào cuộc trò chuyện hiện tại (ghi đè cũ)"""
    valid_docs = []
    if document_ids:
        valid_docs = await chat_service.doc_repo.get_by_ids_and_user(document_ids, current_user.id)
    valid_doc_ids = [doc.id for doc in valid_docs]
    
    await chat_service.chat_repo.set_documents_for_conversation(conversation_id, valid_doc_ids)
    return {"status": "success", "message": f"Đã cập nhật {len(valid_doc_ids)} tài liệu."}
