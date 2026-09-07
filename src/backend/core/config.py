from pathlib import Path
import socket
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CONFIG_DIR.parents[2]
_BACKEND_DIR = _CONFIG_DIR.parent

_env_files = [
    str(_PROJECT_ROOT / ".env"),
    str(_BACKEND_DIR / ".env"),
    ".env",
]

def _resolve_host_to_local(url: str, docker_host: str, local_host: str = "localhost") -> str:
    """Tự động chuyển hostname container (postgres, redis, qdrant) sang localhost khi chạy ngoài Docker."""
    if f"://{docker_host}" in url or f"@{docker_host}" in url:
        try:
            socket.gethostbyname(docker_host)
        except socket.gaierror:
            url = url.replace(f"://{docker_host}", f"://{local_host}").replace(f"@{docker_host}", f"@{local_host}")
    return url

class Settings(BaseSettings):
    # Core system
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    UPLOAD_DIR: str = "/app/data"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Services
    DATABASE_URL: str
    QDRANT_URL: str = "http://qdrant:6333"
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = ""

    # AI Engine (Default: Local Model via Ollama)
    USE_LOCAL_LLM: bool = True
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    GEMINI_API_KEY: str = ""

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
        self.QDRANT_URL = _resolve_host_to_local(self.QDRANT_URL, "qdrant")
        self.REDIS_URL = _resolve_host_to_local(self.REDIS_URL, "redis")
        self.OLLAMA_BASE_URL = _resolve_host_to_local(self.OLLAMA_BASE_URL, "ollama")
        return self

settings = Settings()
