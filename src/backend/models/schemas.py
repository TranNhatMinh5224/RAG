from pydantic import BaseModel, Field
from datetime import datetime

class ChatRequest(BaseModel):
    conversation_id: int
    question: str

class ChatResponse(BaseModel):
    answer: str

class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=6, max_length=70)

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    full_name: str | None = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str = "Đoạn chat mới"
    document_ids: list[int] = [] # Danh sách các file được đính kèm vào cuộc trò chuyện này

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    documents: list[DocumentResponse] = []

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = []

