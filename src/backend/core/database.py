from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings

# Lấy URL từ Settings (đã tự động validate lúc khởi chạy)
DATABASE_URL = settings.DATABASE_URL

# Khởi tạo engine bất đồng bộ với cơ chế tự động ping và làm mới kết nối (tránh timeout từ RDS)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300
)

# Session maker bất đồng bộ
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()
