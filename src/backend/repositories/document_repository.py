from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.document import Document

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> list[Document]:
        result = await self.db.execute(select(Document).filter(Document.user_id == user_id))
        return result.scalars().all()

    async def get_by_id_and_user(self, document_id: int, user_id: int) -> Document | None:
        result = await self.db.execute(select(Document).filter(Document.id == document_id, Document.user_id == user_id))
        return result.scalars().first()

    async def get_by_ids_and_user(self, document_ids: list[int], user_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document).filter(Document.id.in_(document_ids), Document.user_id == user_id)
        )
        return result.scalars().all()

    async def add(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, document: Document):
        from models.chat import ConversationDocument
        from sqlalchemy import delete
        
        # Xóa các liên kết trong bảng trung gian conversation_documents trước để tránh lỗi khóa ngoại (Foreign Key)
        await self.db.execute(
            delete(ConversationDocument).where(ConversationDocument.document_id == document.id)
        )
        await self.db.delete(document)
        await self.db.commit()
