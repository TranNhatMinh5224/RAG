import asyncio
import datetime
from core.config import settings

try:
    import google.generativeai as genai
    from google.generativeai import caching
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Ngưỡng token tối thiểu bắt buộc bởi Google Gemini Context Caching
MIN_CACHE_TOKENS = 32768

class ContextCacheService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.enabled = settings.GEMINI_CACHE_ENABLED
        self.ttl_minutes = settings.GEMINI_CACHE_TTL_MINUTES
        if HAS_GENAI and self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)

    def estimate_tokens(self, text: str) -> int:
        """Ước lượng số token của văn bản (với Tiếng Việt trung bình ~3 ký tự/token)."""
        if not text:
            return 0
        return max(1, len(text) // 3)

    def is_cache_eligible(self, combined_text: str) -> bool:
        """Kiểm tra điều kiện để kích hoạt Gemini Context Cache."""
        if not self.enabled or not HAS_GENAI:
            return False
        return self.estimate_tokens(combined_text) >= MIN_CACHE_TOKENS

    async def get_or_create_cache(
        self,
        conversation_id: int,
        document_texts: list[str],
        existing_cache_name: str | None = None,
        existing_expires_at: datetime.datetime | None = None,
    ) -> tuple[str | None, datetime.datetime | None]:
        """Tạo hoặc tái sử dụng Gemini Context Cache nếu tổng văn bản đạt ngưỡng >= 32k tokens.

        Trả về (cache_name, expires_at) hoặc (None, None) nếu không đủ điều kiện.
        """
        combined = "\n\n".join(document_texts)
        if not self.is_cache_eligible(combined):
            return None, None

        now = datetime.datetime.now(datetime.timezone.utc)

        # Nếu đã có cache và còn hạn sử dụng hơn 5 phút, tái sử dụng
        if existing_cache_name and existing_expires_at:
            if existing_expires_at > now + datetime.timedelta(minutes=5):
                return existing_cache_name, existing_expires_at

        try:
            ttl = datetime.timedelta(minutes=self.ttl_minutes)
            cache = await asyncio.to_thread(
                caching.CachedContent.create,
                model="models/gemini-1.5-flash-001",
                display_name=f"legal_rag_conv_{conversation_id}",
                contents=document_texts,
                ttl=ttl,
            )
            expires_at = now + ttl
            print(f" Đã khởi tạo Gemini Context Cache: {cache.name} (Hết hạn sau {self.ttl_minutes}m)")
            return cache.name, expires_at
        except Exception as e:
            print(f"⚠️ Không thể tạo Gemini Context Cache (Tự động chuyển sang RAG tiêu chuẩn): {e}")
            return None, None
