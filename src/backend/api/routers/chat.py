from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.dependencies import get_chat_service, get_current_user
from models.schemas import ChatRequest, ChatResponse
from models.user import User
from services.chat_service import ChatService
from services.exceptions import ConversationHasNoDocumentsError, ConversationNotFoundError

router = APIRouter(
    prefix="/chat",
    tags=["Chat AI"],
)


@router.post("", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        answer = await chat_service.chat_with_document(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            question=request.question,
            history_limit=5,
        )
        return ChatResponse(answer=answer)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Khong tim thay cuoc tro chuyen")
    except ConversationHasNoDocumentsError:
        raise HTTPException(status_code=400, detail="Cuoc tro chuyen chua dinh kem tai lieu nao.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Khong the xu ly yeu cau chat luc nay")

@router.post("/stream")
async def chat_with_document_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        # Kiểm tra trước để quăng lỗi HTTP sớm nếu không hợp lệ
        chat_context = await chat_service.prepare_chat_context(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            history_limit=5,
        )
        if chat_context is None:
            raise ConversationNotFoundError
        if not chat_context[0]:
            raise ConversationHasNoDocumentsError

        return StreamingResponse(
            chat_service.chat_stream_with_document(
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                question=request.question,
                history_limit=5,
            ),
            media_type="text/event-stream"
        )
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="Khong tim thay cuoc tro chuyen")
    except ConversationHasNoDocumentsError:
        raise HTTPException(status_code=400, detail="Cuoc tro chuyen chua dinh kem tai lieu nao.")
    except Exception:
        raise HTTPException(status_code=500, detail="Khong the xu ly yeu cau stream luc nay")
