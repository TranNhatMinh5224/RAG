from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse
from services.llm_chain import RAGChain
from api.dependencies import get_rag_chain, get_current_user, get_chat_service
from models.user import User
from services.chat_service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat AI"]
)

@router.post("", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    rag_chain: RAGChain = Depends(get_rag_chain),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """API Chat với tài liệu (Bất đồng bộ, Có Memory và Filter)"""
    try:
        # 1. Lấy danh sách Document IDs mà cuộc trò chuyện này được quyền truy cập
        doc_ids = await chat_service.get_conversation_document_ids(current_user.id, request.conversation_id)
        if not doc_ids:
            raise HTTPException(status_code=400, detail="Cuộc trò chuyện này không tồn tại hoặc chưa đính kèm tài liệu nào.")

        # 2. Lấy lịch sử trò chuyện (Memory)
        chat_history = await chat_service.get_conversation_history_str(request.conversation_id, limit=5)

        # 3. Lưu câu hỏi của người dùng vào DB
        await chat_service.save_message(request.conversation_id, role="user", content=request.question)

        # 4. Gửi cho RAG Chain xử lý
        answer = await rag_chain.answer_question_async(
            question=request.question,
            user_id=current_user.id,
            document_ids=doc_ids,
            chat_history=chat_history
        )

        # 5. Lưu câu trả lời của AI vào DB
        await chat_service.save_message(request.conversation_id, role="ai", content=answer)

        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi chat: {str(e)}")
