import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv() # Đọc file .env nếu chạy ở ngoài Docker

# Loại bỏ giá trị mặc định, bắt buộc phải khai báo trong .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("LỖI BẢO MẬT: Chưa khai báo biến môi trường DATABASE_URL trong file .env!")

# Khởi tạo engine bất đồng bộ
engine = create_async_engine(DATABASE_URL, echo=False)

# Session maker bất đồng bộ
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()
