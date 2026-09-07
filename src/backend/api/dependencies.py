from functools import lru_cache
from services.vector_store import VectorStoreManager
from services.retriever import Retriever
from services.llm_chain import RAGChain

@lru_cache()
def get_vector_store() -> VectorStoreManager:
    print("Khởi tạo VectorStoreManager Singleton...")
    return VectorStoreManager()

@lru_cache()
def get_retriever() -> Retriever:
    return Retriever(get_vector_store())

@lru_cache()
def get_rag_chain() -> RAGChain:
    return RAGChain(get_retriever())

# ================= REPOSITORIES & SERVICES DI =================
from core.database import AsyncSessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from core.security import SECRET_KEY, ALGORITHM

from repositories.user_repository import UserRepository
from repositories.document_repository import DocumentRepository
from repositories.chat_repository import ChatRepository
from repositories.activity_repository import ActivityRepository

from services.auth_service import AuthService
from services.document_service import DocumentService
from services.chat_service import ChatService
from services.activity_service import ActivityService

security = HTTPBearer()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

# -- Repositories --
async def get_user_repo(db=Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_document_repo(db=Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)

async def get_chat_repo(db=Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)

async def get_activity_repo(db=Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)

# -- Services --
async def get_activity_service(activity_repo=Depends(get_activity_repo)) -> ActivityService:
    return ActivityService(activity_repo)

async def get_auth_service(
    user_repo=Depends(get_user_repo),
    activity_service=Depends(get_activity_service),
) -> AuthService:
    return AuthService(user_repo, activity_service)

async def get_document_service(
    doc_repo=Depends(get_document_repo),
    vsm=Depends(get_vector_store),
    activity_service=Depends(get_activity_service),
) -> DocumentService:
    return DocumentService(doc_repo, vsm, activity_service)

async def get_chat_service(
    chat_repo=Depends(get_chat_repo),
    doc_repo=Depends(get_document_repo),
    activity_service=Depends(get_activity_service),
) -> ChatService:
    return ChatService(
        chat_repo,
        doc_repo,
        rag_chain_getter=get_rag_chain,
        activity_service=activity_service,
    )


# -- Current User --
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service: AuthService = Depends(get_auth_service)):
    """Kiểm tra JWT Token hợp lệ và trả về User đang đăng nhập"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "access":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token đã hết hạn")
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = await auth_service.get_user_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
