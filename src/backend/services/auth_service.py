from models.user import User
from models.schemas import ChangePasswordRequest, Token, TokenRefresh, UserCreate, UserUpdate
from core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from repositories.user_repository import UserRepository
from services.activity_service import ActivityService
from services.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
)
import jwt

class AuthService:
    def __init__(self, user_repo: UserRepository, activity_service: ActivityService | None = None):
        self.user_repo = user_repo
        self.activity_service = activity_service

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(email=user_data.email, hashed_password=hashed_password)
        return await self.user_repo.add(db_user)

    async def register_user(self, user_data: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise DuplicateEmailError
        new_user = await self.create_user(user_data)
        if self.activity_service:
            await self.activity_service.record_activity(
                action="USER_REGISTER",
                user_id=new_user.id,
                resource_type="user",
                resource_id=str(new_user.id),
                details=f"Đăng ký tài khoản: {new_user.email}",
            )
        return new_user

    async def authenticate_user(self, email: str, password: str) -> User | bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    async def login(self, email: str, password: str) -> Token:
        auth_user = await self.authenticate_user(email, password)
        if not auth_user:
            raise AuthenticationError

        if self.activity_service:
            await self.activity_service.record_activity(
                action="USER_LOGIN",
                user_id=auth_user.id,
                resource_type="user",
                resource_id=str(auth_user.id),
                details=f"Đăng nhập thành công: {auth_user.email}",
            )

        return Token(
            access_token=create_access_token(data={"sub": auth_user.email}),
            refresh_token=create_refresh_token(data={"sub": auth_user.email}),
            token_type="bearer",
        )

    async def refresh_tokens(self, token_data: TokenRefresh) -> Token:
        try:
            payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("token_type") != "refresh":
                raise InvalidRefreshTokenError
            email: str = payload.get("sub")
            if email is None:
                raise InvalidRefreshTokenError
        except jwt.PyJWTError:
            raise InvalidRefreshTokenError

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise InvalidRefreshTokenError

        return Token(
            access_token=create_access_token(data={"sub": user.email}),
            refresh_token=create_refresh_token(data={"sub": user.email}),
            token_type="bearer",
        )

    async def update_password(self, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        return await self.user_repo.update(user)

    async def change_password(self, user: User, request: ChangePasswordRequest) -> None:
        if not verify_password(request.old_password, user.hashed_password):
            raise InvalidPasswordError
        await self.update_password(user, request.new_password)

    async def update_user_info(self, user: User, full_name: str | None) -> User:
        if full_name is not None:
            user.full_name = full_name
        return await self.user_repo.update(user)

    async def update_profile(self, user: User, update_data: UserUpdate) -> User:
        return await self.update_user_info(user, update_data.full_name)
