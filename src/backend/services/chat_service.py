import os
import datetime
from dataclasses import dataclass
from models.chat import Conversation, Message
from models.user import User
from repositories.chat_repository import ChatRepository
from repositories.document_repository import DocumentRepository
from services.exceptions import ConversationHasNoDocumentsError, ConversationNotFoundError
from services.context_cache_service import ContextCacheService
from services.activity_service import ActivityService
from core.config import settings
from core.logger import get_logger, get_request_id

logger = get_logger("services.chat_service")


@dataclass
class ChatContext:
    document_ids: list[int]
    chat_history: str
    summary: str = ""
    gemini_cache_name: str | None = None

    def __getitem__(self, index):
        if index == 0:
            return self.document_ids
        elif index == 1:
            return self.chat_history
        elif index == 2:
            return self.summary
        elif index == 3:
            return self.gemini_cache_name
        raise IndexError("ChatContext index out of range")


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        doc_repo: DocumentRepository,
        rag_chain=None,
        rag_chain_getter=None,
        cache_service: ContextCacheService | None = None,
        activity_service: ActivityService | None = None,
    ):
        self.chat_repo = chat_repo
        self.doc_repo = doc_repo
        self._rag_chain = rag_chain
        self.rag_chain_getter = rag_chain_getter
        self.cache_service = cache_service or ContextCacheService()
        self.activity_service = activity_service

    @property
    def rag_chain(self):
        if self._rag_chain is None and self.rag_chain_getter is not None:
            self._rag_chain = self.rag_chain_getter()
        return self._rag_chain

    async def create_conversation(
        self,
        user: User,
        title: str,
        document_ids: list[int],
    ) -> Conversation:
        new_conv = Conversation(user_id=user.id, title=title)
        new_conv = await self.chat_repo.create_conversation(new_conv)

        if document_ids:
            valid_docs = await self.doc_repo.get_by_ids_and_user(document_ids, user.id)
            valid_doc_ids = [doc.id for doc in valid_docs]
            if valid_doc_ids:
                await self.chat_repo.set_documents_for_conversation(new_conv.id, valid_doc_ids)

        conv = await self.chat_repo.get_conversation_with_documents(new_conv.id, user.id)

        if self.activity_service:
            await self.activity_service.record_activity(
                action="CONVERSATION_CREATE",
                user_id=user.id,
                resource_type="conversation",
                resource_id=str(new_conv.id),
                details=f"Tạo cuộc trò chuyện: {title}",
            )

        return conv

    async def get_user_conversations(self, user_id: int) -> list[Conversation]:
        return await self.chat_repo.get_user_conversations(user_id)

    async def delete_conversation(self, user_id: int, conversation_id: int) -> bool:
        conv = await self.chat_repo.get_conversation_with_documents(conversation_id, user_id)
        if conv:
            await self.chat_repo.delete_conversation(conv)
            return True
        return False

    async def delete_conversation_or_raise(self, user_id: int, conversation_id: int) -> None:
        conv = await self.chat_repo.get_conversation_with_documents(conversation_id, user_id)
        if conv is None:
            raise ConversationNotFoundError
        await self.chat_repo.delete_conversation(conv)
        logger.info(f"Đã xóa cuộc trò chuyện {conversation_id} của user {user_id}")

        if self.activity_service:
            await self.activity_service.record_activity(
                action="CONVERSATION_DELETE",
                user_id=user_id,
                resource_type="conversation",
                resource_id=str(conversation_id),
                details=f"Xóa cuộc trò chuyện: {conv.title}",
            )

    async def get_conversation_document_ids(
        self,
        user_id: int,
        conversation_id: int,
    ) -> list[int]:
        conv = await self.chat_repo.get_conversation_with_documents(conversation_id, user_id)
        if not conv:
            return []
        return [doc.id for doc in conv.documents]

    async def get_conversation_details(
        self,
        user_id: int,
        conversation_id: int,
        message_limit: int = 50,
    ) -> dict | None:
        conversation = await self.chat_repo.get_conversation_with_documents(
            conversation_id,
            user_id,
        )
        if conversation is None:
            return None

        messages = await self.chat_repo.get_recent_messages_for_user(
            conversation_id,
            user_id,
            limit=message_limit,
        )
        return {
            "id": conversation.id,
            "title": conversation.title,
            "summary": conversation.summary,
            "created_at": conversation.created_at,
            "documents": conversation.documents,
            "messages": messages,
        }

    async def get_conversation_details_or_raise(
        self,
        user_id: int,
        conversation_id: int,
        message_limit: int = 50,
    ) -> dict:
        conversation = await self.get_conversation_details(
            user_id=user_id,
            conversation_id=conversation_id,
            message_limit=message_limit,
        )
        if conversation is None:
            raise ConversationNotFoundError
        return conversation

    async def attach_documents(
        self,
        user_id: int,
        conversation_id: int,
        document_ids: list[int],
    ) -> int | None:
        """Replace a conversation's documents after verifying tenant ownership.

        Returns the number of attached documents, or ``None`` when the
        conversation does not belong to the current user.
        """
        conversation = await self.chat_repo.get_conversation_with_documents(
            conversation_id,
            user_id,
        )
        if conversation is None:
            return None

        valid_documents = []
        if document_ids:
            valid_documents = await self.doc_repo.get_by_ids_and_user(
                document_ids,
                user_id,
            )

        valid_document_ids = [document.id for document in valid_documents]
        await self.chat_repo.set_documents_for_conversation(
            conversation.id,
            valid_document_ids,
        )
        return len(valid_document_ids)

    async def attach_documents_or_raise(
        self,
        user_id: int,
        conversation_id: int,
        document_ids: list[int],
    ) -> int:
        attached_count = await self.attach_documents(user_id, conversation_id, document_ids)
        if attached_count is None:
            raise ConversationNotFoundError
        return attached_count

    async def prepare_chat_context(
        self,
        user_id: int,
        conversation_id: int,
        history_limit: int | None = None,
    ) -> ChatContext | None:
        conversation = await self.chat_repo.get_conversation_with_documents(
            conversation_id,
            user_id,
        )
        if conversation is None:
            return None

        effective_limit = history_limit if history_limit is not None else settings.RECENT_MESSAGES_WINDOW

        document_ids = [document.id for document in conversation.documents]
        messages = await self.chat_repo.get_recent_messages_for_user(
            conversation_id,
            user_id,
            limit=effective_limit,
        )
        formatted_history = self._format_history(messages)
        summary = conversation.summary or ""

        # Kiểm tra Gemini Context Cache nếu được cấu hình
        cache_name = conversation.gemini_cache_name
        if self.cache_service and settings.GEMINI_CACHE_ENABLED and document_ids:
            now = datetime.datetime.now(datetime.timezone.utc)
            if not cache_name or not conversation.gemini_cache_expires_at or conversation.gemini_cache_expires_at <= now:
                doc_texts = []
                for doc in conversation.documents:
                    if doc.file_path and os.path.exists(doc.file_path):
                        try:
                            if doc.file_path.endswith(".txt"):
                                with open(doc.file_path, "r", encoding="utf-8", errors="ignore") as f:
                                    doc_texts.append(f.read())
                        except Exception:
                            pass
                if doc_texts:
                    new_cache_name, expires_at = await self.cache_service.get_or_create_cache(
                        conversation_id=conversation.id,
                        document_texts=doc_texts,
                        existing_cache_name=conversation.gemini_cache_name,
                        existing_expires_at=conversation.gemini_cache_expires_at,
                    )
                    if new_cache_name:
                        await self.chat_repo.update_gemini_cache(
                            conversation_id=conversation.id,
                            user_id=user_id,
                            cache_name=new_cache_name,
                            expires_at=expires_at,
                        )
                        cache_name = new_cache_name

        return ChatContext(
            document_ids=document_ids,
            chat_history=formatted_history,
            summary=summary,
            gemini_cache_name=cache_name,
        )

    async def chat_with_document(
        self,
        user_id: int,
        conversation_id: int,
        question: str,
        history_limit: int | None = None,
    ) -> str:
        if self.rag_chain is None:
            raise RuntimeError("RAG chain is not configured")

        chat_context = await self.prepare_chat_context(
            user_id=user_id,
            conversation_id=conversation_id,
            history_limit=history_limit,
        )
        if chat_context is None:
            raise ConversationNotFoundError

        document_ids = chat_context.document_ids
        chat_history = chat_context.chat_history
        summary = chat_context.summary
        cached_content = chat_context.gemini_cache_name

        if not document_ids:
            raise ConversationHasNoDocumentsError

        await self.save_message(conversation_id, role="user", content=question)

        answer = await self.rag_chain.answer_question_async(
            question=question,
            user_id=user_id,
            document_ids=document_ids,
            chat_history=chat_history,
            conversation_id=conversation_id,
            conversation_summary=summary,
            cached_content=cached_content,
        )

        await self.save_message(conversation_id, role="ai", content=answer)

        # Tự động tóm tắt nếu số tin nhắn vượt ngưỡng
        await self.trigger_summarization_if_needed(conversation_id, user_id)

        return answer

    async def chat_stream_with_document(
        self,
        user_id: int,
        conversation_id: int,
        question: str,
        history_limit: int | None = None,
    ):
        if self.rag_chain is None:
            raise RuntimeError("RAG chain is not configured")

        chat_context = await self.prepare_chat_context(
            user_id=user_id,
            conversation_id=conversation_id,
            history_limit=history_limit,
        )
        if chat_context is None:
            raise ConversationNotFoundError

        document_ids = chat_context.document_ids
        chat_history = chat_context.chat_history
        summary = chat_context.summary
        cached_content = chat_context.gemini_cache_name

        if not document_ids:
            raise ConversationHasNoDocumentsError

        # Lưu câu hỏi của người dùng
        await self.save_message(conversation_id, role="user", content=question)

        full_answer = ""
        # Đọc dữ liệu stream từ Langchain
        async for chunk in self.rag_chain.answer_question_stream(
            question=question,
            user_id=user_id,
            document_ids=document_ids,
            chat_history=chat_history,
            conversation_id=conversation_id,
            conversation_summary=summary,
            cached_content=cached_content,
        ):
            full_answer += chunk
            yield chunk

        # Lưu toàn bộ câu trả lời của AI vào DB khi stream kết thúc
        await self.save_message(conversation_id, role="ai", content=full_answer)

        # Tự động tóm tắt nếu số tin nhắn vượt ngưỡng
        await self.trigger_summarization_if_needed(conversation_id, user_id)

    async def trigger_summarization_if_needed(self, conversation_id: int, user_id: int) -> str | None:
        """Kiểm tra nếu số tin nhắn >= SUMMARIZATION_THRESHOLD (10), tự động tóm tắt các tin nhắn cũ."""
        total_count = await self.chat_repo.count_messages_for_user(conversation_id, user_id)
        if total_count < settings.SUMMARIZATION_THRESHOLD:
            return None

        old_messages = await self.chat_repo.get_messages_before_recent_for_user(
            conversation_id,
            user_id,
            exclude_recent_count=settings.RECENT_MESSAGES_WINDOW,
        )
        if not old_messages:
            return None

        conv = await self.chat_repo.get_conversation_with_documents(conversation_id, user_id)
        if not conv:
            return None

        formatted_old = self._format_history(old_messages)
        if self.rag_chain:
            logger.info(f"Đang tóm tắt ngầm {len(old_messages)} tin nhắn cũ cho cuộc trò chuyện {conversation_id}...")
            new_summary = await self.rag_chain.generate_conversation_summary_async(
                existing_summary=conv.summary,
                messages_text=formatted_old,
                user_id=user_id,
                session_id=conversation_id,
            )
            if new_summary:
                await self.chat_repo.update_conversation_summary(conversation_id, user_id, new_summary)
                logger.info(f"Hoàn tất cập nhật tóm tắt hội thoại cho conversation {conversation_id}")
                return new_summary
        return None

    async def get_conversation_history_str(
        self,
        conversation_id: int,
        limit: int = 5,
    ) -> str:
        messages = await self.chat_repo.get_recent_messages(conversation_id, limit)
        return self._format_history(messages)

    async def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> Message:
        new_msg = Message(conversation_id=conversation_id, role=role, content=content)
        return await self.chat_repo.add_message(new_msg)

    def _format_history(self, messages: list[Message]) -> str:
        history_str = ""
        for msg in messages:
            role = "Nguoi dung" if msg.role == "user" else "AI"
            history_str += f"{role}: {msg.content}\n"
        return history_str

