from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings

# Lấy URL từ Settings (đã tự động validate lúc khởi chạy)
DATABASE_URL = settings.DATABASE_URL

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
