import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

load_dotenv()

# Bắt buộc phải khai báo trong .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("LỖI BẢO MẬT: Chưa khai báo biến môi trường SECRET_KEY trong file .env!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Cấu hình Bcrypt để băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    truncated = plain_password.encode('utf-8')[:64].decode('utf-8', 'ignore')
    return pwd_context.verify(truncated, hashed_password)

def get_password_hash(password):
    truncated = password.encode('utf-8')[:64].decode('utf-8', 'ignore')
    return pwd_context.hash(truncated)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
