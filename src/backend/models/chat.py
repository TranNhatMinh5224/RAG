from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

# Bảng trung gian Many-to-Many giữa Cuộc trò chuyện và Tài liệu
class ConversationDocument(Base):
    __tablename__ = "conversation_documents"
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="Đoạn chat mới")
    summary = Column(Text, nullable=True)
    gemini_cache_name = Column(String, nullable=True)
    gemini_cache_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Các mối quan hệ
    owner = relationship("User", back_populates="conversations")
    documents = relationship("Document", secondary="conversation_documents", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False) # 'user' hoặc 'ai'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
