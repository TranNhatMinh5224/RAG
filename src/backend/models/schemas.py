from pydantic import BaseModel, Field
from datetime import datetime

class ChatRequest(BaseModel):
    conversation_id: int
    question: str = Field(..., min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    answer: str

class StatusResponse(BaseModel):
    status: str
    message: str

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

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=70)

class UserUpdate(BaseModel):
    full_name: str | None = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    status: str | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str = "Đoạn chat mới"
    document_ids: list[int] = Field(default_factory=list)

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    documents: list[DocumentResponse] = Field(default_factory=list)

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
    messages: list[MessageResponse] = Field(default_factory=list)


class ActivityLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    details: str | None = None
    ip_address: str | None = None
    request_id: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


