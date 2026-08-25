from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core system
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: str = ""
    UPLOAD_DIR: str = "/app/data"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Services
    DATABASE_URL: str
    QDRANT_URL: str = "http://qdrant:6333"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    # AI
    GEMINI_API_KEY: str
    USE_LOCAL_LLM: bool = False
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
