from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
import models.user
import models.document
import models.chat
from core.config import settings

app = FastAPI(
    title="RAG Chatbot API - Clean Architecture",
    description="Hệ thống hỏi đáp tài liệu chuẩn Production (100% Async)",
    version="1.0.0"
)

# Sự kiện lúc khởi động: Tạo bảng CSDL bất đồng bộ
@app.on_event("startup")
async def startup_event():
    print(" Đang khởi động Server...")
    # Tính năng tự động tạo bảng Base.metadata.create_all đã được tắt.
    # Kể từ bây giờ, cấu trúc bảng CSDL sẽ được quản lý bằng lệnh Alembic Migration.
    print(" Web Server đã sẵn sàng!")



allowed_origins_str = settings.ALLOWED_ORIGINS
allowed_origins = [url.strip() for url in allowed_origins_str.split(",") if url.strip()]

if not allowed_origins:
    print("⚠️ CẢNH BÁO BẢO MẬT: ALLOWED_ORIGINS trống. Web sẽ chặn mọi truy cập từ Frontend!")

# Cấu hình CORS an toàn
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # Chỉ cho phép đúng danh sách Domain khai báo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers từ Layer API
from api.routers import document, chat, auth, conversation

# Gắn (Include) các routers vào ứng dụng chính
app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(document.router)
app.include_router(chat.router)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Hệ thống RAG Backend đang hoạt động trơn tru!"}