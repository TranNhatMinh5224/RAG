from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.schemas import UserCreate, UserResponse, Token, TokenRefresh, ForgotPasswordRequest, ChangePasswordRequest, UserUpdate
from api.dependencies import get_current_user, get_auth_service
from services.auth_service import AuthService
from core.security import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM, verify_password
from models.user import User
import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """Đăng ký tài khoản mới (Bất đồng bộ)"""
    db_user = await auth_service.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
    new_user = await auth_service.create_user(user_data=user)
    return new_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    """Đăng nhập để nhận Access Token và Refresh Token (Bất đồng bộ)"""
    auth_user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": auth_user.email})
    refresh_token = create_refresh_token(data={"sub": auth_user.email})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(token_data: TokenRefresh, auth_service: AuthService = Depends(get_auth_service)):
    """Đổi Refresh Token lấy Access Token mới (Bất đồng bộ)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = await auth_service.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
        
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập (Bất đồng bộ)"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(update_data: UserUpdate, current_user: User = Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)):
    """Cập nhật thông tin cá nhân (Tên đầy đủ)"""
    updated_user = await auth_service.update_user_info(current_user, update_data.full_name)
    return updated_user

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)):
    """Đổi mật khẩu (Yêu cầu đang đăng nhập và biết mật khẩu cũ)"""
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
    
    await auth_service.update_password(current_user, request.new_password)
    return {"status": "success", "message": "Đã đổi mật khẩu thành công"}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Quên mật khẩu: Đặt lại mật khẩu mới nếu nhập đúng Email đã đăng ký"""
    user = await auth_service.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản với Email này")
    
    await auth_service.update_password(user, request.new_password)
    return {"status": "success", "message": "Đã đặt lại mật khẩu mới thành công"}
