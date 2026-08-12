from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_chat_service, get_current_user
from models.schemas import ConversationCreate, ConversationDetailResponse, ConversationResponse, StatusResponse
from models.user import User
from services.chat_service import ChatService
from services.exceptions import ConversationNotFoundError

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation Management"],
)


@router.post("/", response_model=ConversationResponse)
async def create_new_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        return await chat_service.create_conversation(
            current_user,
            request.title,
            request.document_ids,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Khong the tao cuoc tro chuyen")


@router.get("/list", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_user_conversations(current_user.id)


@router.delete("/{conversation_id}", response_model=StatusResponse)
async def delete_conversation_api(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        await chat_service.delete_conversation_or_raise(current_user.id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Khong tim thay cuoc tro chuyen")
    return {"status": "success", "message": "Da xoa cuoc tro chuyen"}


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_details(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        return await chat_service.get_conversation_details_or_raise(
            user_id=current_user.id,
            conversation_id=conversation_id,
            message_limit=50,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Khong tim thay cuoc tro chuyen")


@router.post("/{conversation_id}/documents", response_model=StatusResponse)
async def attach_documents(
    conversation_id: int,
    document_ids: list[int],
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        attached_count = await chat_service.attach_documents_or_raise(
            user_id=current_user.id,
            conversation_id=conversation_id,
            document_ids=document_ids,
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Khong tim thay cuoc tro chuyen")

    return {
        "status": "success",
        "message": f"Da cap nhat {attached_count} tai lieu.",
    }
