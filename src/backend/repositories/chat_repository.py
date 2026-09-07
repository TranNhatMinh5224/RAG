from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.chat import Conversation, Message, ConversationDocument

class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def set_documents_for_conversation(self, conversation_id: int, document_ids: list[int]):
        from sqlalchemy import delete
        # Xóa các liên kết cũ
        await self.db.execute(
            delete(ConversationDocument).where(ConversationDocument.conversation_id == conversation_id)
        )
        # Thêm các liên kết mới
        for doc_id in document_ids:
            conv_doc = ConversationDocument(conversation_id=conversation_id, document_id=doc_id)
            self.db.add(conv_doc)
        await self.db.commit()

    async def get_conversation_with_documents(self, conversation_id: int, user_id: int) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.documents))
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalars().first()

    async def get_user_conversations(self, user_id: int) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.documents))
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()

    async def delete_conversation(self, conversation: Conversation):
        await self.db.delete(conversation)
        await self.db.commit()

    async def get_recent_messages(self, conversation_id: int, limit: int = 5) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        messages.reverse()
        return messages

    async def get_recent_messages_for_user(
        self,
        conversation_id: int,
        user_id: int,
        limit: int = 5,
    ) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Message.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        messages.reverse()
        return messages

    async def add_message(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def count_messages_for_user(self, conversation_id: int, user_id: int) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Message.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one() or 0

    async def get_messages_before_recent_for_user(
        self,
        conversation_id: int,
        user_id: int,
        exclude_recent_count: int = 4,
    ) -> list[Message]:
        total = await self.count_messages_for_user(conversation_id, user_id)
        if total <= exclude_recent_count:
            return []
        limit_count = total - exclude_recent_count
        result = await self.db.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Message.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .order_by(Message.created_at.asc())
            .limit(limit_count)
        )
        return list(result.scalars().all())

    async def update_conversation_summary(
        self,
        conversation_id: int,
        user_id: int,
        summary: str,
    ) -> Conversation | None:
        conv = await self.get_conversation_with_documents(conversation_id, user_id)
        if conv:
            conv.summary = summary
            await self.db.commit()
            await self.db.refresh(conv)
        return conv

    async def update_gemini_cache(
        self,
        conversation_id: int,
        user_id: int,
        cache_name: str,
        expires_at,
    ) -> Conversation | None:
        conv = await self.get_conversation_with_documents(conversation_id, user_id)
        if conv:
            conv.gemini_cache_name = cache_name
            conv.gemini_cache_expires_at = expires_at
            await self.db.commit()
            await self.db.refresh(conv)
        return conv

