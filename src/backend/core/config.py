import json
import os
from pathlib import Path
import socket
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CONFIG_DIR.parent
_PROJECT_ROOT = _CONFIG_DIR.parents[2] if len(_CONFIG_DIR.parents) > 2 else _BACKEND_DIR

_env_files = [
    str(_PROJECT_ROOT / ".env"),
    str(_BACKEND_DIR / ".env"),
    ".env",
]

def _fetch_aws_secrets(secret_name: str = "rag/production/credentials", region_name: str = "ap-southeast-1"):
    """Tự động tải cấu hình trực tiếp từ AWS Secrets Manager qua IAM Role của EC2."""
    try:
        import boto3
        region = os.environ.get("AWS_REGION", region_name)
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            secrets = json.loads(response["SecretString"])
            for key, val in secrets.items():
                if key not in os.environ:
                    os.environ[key] = str(val)
            print(f"[AWS Secrets Manager] Đã nạp thành công các cấu hình từ '{secret_name}' vào bộ nhớ!")
    except Exception:
        # Nếu đang chạy local offline hoặc chưa có quyền AWS, tự động fallback sang file .env
        pass

# Tự động nạp secret từ AWS Secrets Manager ngay khi khởi động
_fetch_aws_secrets()

def _resolve_host_to_local(url: str, docker_host: str, local_host: str = "localhost") -> str:
    """Tự động chuyển hostname container (postgres, redis, qdrant) sang localhost khi chạy ngoài Docker."""
    if not url:
        return url
    try:
        import urllib.parse
        parsed = urllib.parse.urlsplit(url)
        if parsed.hostname == docker_host:
            try:
                socket.gethostbyname(docker_host)
            except socket.gaierror:
                netloc = parsed.netloc.replace(f"@{docker_host}", f"@{local_host}")
                if parsed.netloc == docker_host:
                    netloc = local_host
                return urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    except Exception:
        pass
    return url

class Settings(BaseSettings):
    # Core system
    SECRET_KEY: str = "enterprise_rag_jwt_secret_key_production_2026_super_secure!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    UPLOAD_DIR: str = "/app/data"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Services
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    QDRANT_URL: str = "http://qdrant:6333"
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = ""

    # AWS S3 Storage
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: str = "enterprise-rag-storage-0117967"
    DOCUMENTS_DRAFT_PREFIX: str = "documents/draft/"
    DOCUMENTS_REAL_PREFIX: str = "documents/real/"

    # AI Engine (Default: Local Model via Ollama)
    USE_LOCAL_LLM: bool = False
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    GEMINI_API_KEY: str = ""

    # Amazon Bedrock (Mantle Endpoint)
    USE_BEDROCK: bool = False
    BEDROCK_API_KEY: str = ""
    BEDROCK_BASE_URL: str = "https://bedrock-mantle.us-east-1.api.aws/v1"
    BEDROCK_MODEL: str = "mistral.ministral-3-14b-instruct"

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Context Optimization & Summarization
    SUMMARIZATION_THRESHOLD: int = 10
    RECENT_MESSAGES_WINDOW: int = 4
    GEMINI_CACHE_ENABLED: bool = False
    GEMINI_CACHE_TTL_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=_env_files, env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def adjust_service_urls(self):
        self.DATABASE_URL = _resolve_host_to_local(self.DATABASE_URL, "postgres")
        if "rds.amazonaws.com" in self.DATABASE_URL and "ssl=" not in self.DATABASE_URL:
            sep = "&" if "?" in self.DATABASE_URL else "?"
            self.DATABASE_URL = f"{self.DATABASE_URL}{sep}ssl=require"
        self.QDRANT_URL = _resolve_host_to_local(self.QDRANT_URL, "qdrant")
        self.REDIS_URL = _resolve_host_to_local(self.REDIS_URL, "redis")
        self.OLLAMA_BASE_URL = _resolve_host_to_local(self.OLLAMA_BASE_URL, "ollama")
        return self

settings = Settings()
