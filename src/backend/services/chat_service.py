from models.chat import Conversation, Message
from models.user import User
from repositories.chat_repository import ChatRepository
from repositories.document_repository import DocumentRepository
from services.exceptions import ConversationHasNoDocumentsError, ConversationNotFoundError


class ChatService:
    def __init__(self, chat_repo: ChatRepository, doc_repo: DocumentRepository, rag_chain=None):
        self.chat_repo = chat_repo
        self.doc_repo = doc_repo
        self.rag_chain = rag_chain

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

        return await self.chat_repo.get_conversation_with_documents(new_conv.id, user.id)

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
        history_limit: int = 5,
    ) -> tuple[list[int], str] | None:
        conversation = await self.chat_repo.get_conversation_with_documents(
            conversation_id,
            user_id,
        )
        if conversation is None:
            return None

        document_ids = [document.id for document in conversation.documents]
        messages = await self.chat_repo.get_recent_messages_for_user(
            conversation_id,
            user_id,
            limit=history_limit,
        )
        return document_ids, self._format_history(messages)

    async def chat_with_document(
        self,
        user_id: int,
        conversation_id: int,
        question: str,
        history_limit: int = 5,
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

        document_ids, chat_history = chat_context
        if not document_ids:
            raise ConversationHasNoDocumentsError

        await self.save_message(conversation_id, role="user", content=question)

        answer = await self.rag_chain.answer_question_async(
            question=question,
            user_id=user_id,
            document_ids=document_ids,
            chat_history=chat_history,
        )

        await self.save_message(conversation_id, role="ai", content=answer)
        return answer

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
