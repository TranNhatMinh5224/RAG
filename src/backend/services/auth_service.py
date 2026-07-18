from models.user import User
from models.schemas import UserCreate
from core.security import get_password_hash, verify_password
from repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(email=user_data.email, hashed_password=hashed_password)
        return await self.user_repo.add(db_user)

    async def authenticate_user(self, email: str, password: str) -> User | bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    async def update_password(self, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        return await self.user_repo.update(user)

    async def update_user_info(self, user: User, full_name: str | None) -> User:
        if full_name is not None:
            user.full_name = full_name
        return await self.user_repo.update(user)
