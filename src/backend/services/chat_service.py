from models.chat import Conversation, Message
from models.user import User
from repositories.chat_repository import ChatRepository
from repositories.document_repository import DocumentRepository

class ChatService:
    def __init__(self, chat_repo: ChatRepository, doc_repo: DocumentRepository):
        self.chat_repo = chat_repo
        self.doc_repo = doc_repo

    async def create_conversation(self, user: User, title: str, document_ids: list[int]) -> Conversation:
        new_conv = Conversation(user_id=user.id, title=title)
        new_conv = await self.chat_repo.create_conversation(new_conv)

        if document_ids:
            # Lấy danh sách doc hợp lệ thuộc về user
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

    async def get_conversation_document_ids(self, user_id: int, conversation_id: int) -> list[int]:
        conv = await self.chat_repo.get_conversation_with_documents(conversation_id, user_id)
        if not conv:
            return []
        return [doc.id for doc in conv.documents]

    async def get_conversation_history_str(self, conversation_id: int, limit: int = 5) -> str:
        messages = await self.chat_repo.get_recent_messages(conversation_id, limit)
        history_str = ""
        for msg in messages:
            role = "Người dùng" if msg.role == "user" else "AI"
            history_str += f"{role}: {msg.content}\n"
        return history_str

    async def save_message(self, conversation_id: int, role: str, content: str) -> Message:
        new_msg = Message(conversation_id=conversation_id, role=role, content=content)
        return await self.chat_repo.add_message(new_msg)
