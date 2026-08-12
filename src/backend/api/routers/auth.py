from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_auth_service, get_current_user
from models.schemas import ChangePasswordRequest, StatusResponse, Token, TokenRefresh, UserCreate, UserResponse, UserUpdate
from models.user import User
from services.auth_service import AuthService
from services.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.register_user(user)
    except DuplicateEmailError:
        raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.login(form_data.username, form_data.password)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.refresh_tokens(token_data)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.update_profile(current_user, update_data)


@router.post("/change-password", response_model=StatusResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        await auth_service.change_password(current_user, request)
        return {"status": "success", "message": "Password changed successfully"}
    except InvalidPasswordError:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
