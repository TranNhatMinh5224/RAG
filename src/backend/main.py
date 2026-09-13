from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
import models.user
import models.document
import models.chat
import models.activity_log
from core.config import settings
from core.logger import setup_logging, get_logger
from core.middleware import RequestLoggingMiddleware

# Khởi tạo hệ thống Structured Logging (CloudWatch & Rotating File)
setup_logging()
logger = get_logger("main")

app = FastAPI(
    title="RAG Chatbot API - Clean Architecture",
    description="Hệ thống hỏi đáp tài liệu chuẩn Production (100% Async)",
    version="1.0.1"
)

# Gắn Request Logging Middleware (Gắn X-Request-ID và đo latency)
app.add_middleware(RequestLoggingMiddleware)

# Sự kiện lúc khởi động
@app.on_event("startup")
async def startup_event():
    logger.info("Đang khởi động Server...")
    logger.info("Web Server đã sẵn sàng phục vụ!")

allowed_origins_str = settings.ALLOWED_ORIGINS
allowed_origins = [url.strip() for url in allowed_origins_str.split(",") if url.strip()]

# Đảm bảo luôn hỗ trợ môi trường dev cục bộ (Next.js 3000, 127.0.0.1:3000)
for dev_url in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]:
    if dev_url not in allowed_origins:
        allowed_origins.append(dev_url)

# Cấu hình CORS an toàn
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers từ Layer API
from api.routers import document, chat, auth, conversation, activity

# Gắn (Include) các routers vào ứng dụng chính
app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(document.router)
app.include_router(chat.router)
app.include_router(activity.router)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "Hệ thống RAG Backend đang hoạt động trơn tru!"}