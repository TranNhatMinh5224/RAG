import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Đảm bảo đường dẫn import src/backend được thêm vào sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.context_cache_service import ContextCacheService, MIN_CACHE_TOKENS
from services.chat_service import ChatService, ChatContext
from models.chat import Conversation, Message
from core.config import settings


class TestContextCacheService(unittest.TestCase):
    def setUp(self):
        self.service = ContextCacheService(api_key="test_key")

    def test_estimate_tokens(self):
        text = "Đây là một đoạn văn bản tiếng Việt để kiểm tra số lượng token ước lượng."
        tokens = self.service.estimate_tokens(text)
        self.assertGreater(tokens, 0)
        self.assertEqual(tokens, len(text) // 3)

    def test_estimate_tokens_empty(self):
        self.assertEqual(self.service.estimate_tokens(""), 0)

    def test_is_cache_eligible_short_text(self):
        # Văn bản ngắn (< 32k tokens) không đủ điều kiện tạo cache
        short_text = "Văn bản ngắn không đủ 32768 tokens."
        self.assertFalse(self.service.is_cache_eligible(short_text))

    def test_is_cache_eligible_long_text(self):
        # Tạo văn bản đủ lớn (>= 32768 tokens)
        long_text = "Quy định pháp luật " * 15000
        with patch.object(self.service, "enabled", True):
            with patch("services.context_cache_service.HAS_GENAI", True):
                self.assertTrue(self.service.is_cache_eligible(long_text))


class TestChatContextDataclass(unittest.TestCase):
    def test_chat_context_indexing_and_attributes(self):
        ctx = ChatContext(
            document_ids=[1, 2],
            chat_history="User: Hello\nAI: Hi",
            summary="Đã chào hỏi",
            gemini_cache_name="cache_123",
        )
        self.assertEqual(ctx[0], [1, 2])
        self.assertEqual(ctx[1], "User: Hello\nAI: Hi")
        self.assertEqual(ctx[2], "Đã chào hỏi")
        self.assertEqual(ctx[3], "cache_123")
        self.assertEqual(ctx.document_ids, [1, 2])
        self.assertEqual(ctx.summary, "Đã chào hỏi")
        self.assertEqual(ctx.gemini_cache_name, "cache_123")

        with self.assertRaises(IndexError):
            _ = ctx[4]


class TestChatServiceSummarization(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_chat_repo = AsyncMock()
        self.mock_doc_repo = AsyncMock()
        self.mock_rag_chain = AsyncMock()
        self.mock_cache_service = AsyncMock()

        self.service = ChatService(
            chat_repo=self.mock_chat_repo,
            doc_repo=self.mock_doc_repo,
            rag_chain=self.mock_rag_chain,
            cache_service=self.mock_cache_service,
        )

    async def test_prepare_chat_context_uses_recent_window_and_summary(self):
        mock_conv = MagicMock()
        mock_conv.id = 1
        mock_conv.summary = "Bản tóm tắt trước đó"
        mock_conv.gemini_cache_name = None
        mock_conv.gemini_cache_expires_at = None
        mock_conv.documents = []
        self.mock_chat_repo.get_conversation_with_documents.return_value = mock_conv

        mock_msg = MagicMock()
        mock_msg.role = "user"
        mock_msg.content = "Xin chào"
        self.mock_chat_repo.get_recent_messages_for_user.return_value = [mock_msg]

        ctx = await self.service.prepare_chat_context(user_id=10, conversation_id=1)

        self.assertIsNotNone(ctx)
        self.assertEqual(ctx.summary, "Bản tóm tắt trước đó")
        self.assertIn("Nguoi dung: Xin chào", ctx.chat_history)
        self.mock_chat_repo.get_recent_messages_for_user.assert_called_once_with(
            1, 10, limit=settings.RECENT_MESSAGES_WINDOW
        )

    async def test_trigger_summarization_below_threshold(self):
        # Dưới ngưỡng 10 tin nhắn -> không kích hoạt tóm tắt
        self.mock_chat_repo.count_messages_for_user.return_value = 8

        result = await self.service.trigger_summarization_if_needed(conversation_id=1, user_id=10)

        self.assertIsNone(result)
        self.mock_rag_chain.generate_conversation_summary_async.assert_not_called()

    async def test_trigger_summarization_above_threshold(self):
        # Vượt ngưỡng 10 tin nhắn (ví dụ 12 tin nhắn)
        self.mock_chat_repo.count_messages_for_user.return_value = 12

        old_msg1 = MagicMock(role="user", content="Hỏi về Luật Doanh nghiệp 2020")
        old_msg2 = MagicMock(role="ai", content="Luật Doanh nghiệp quy định...")
        self.mock_chat_repo.get_messages_before_recent_for_user.return_value = [old_msg1, old_msg2]

        mock_conv = MagicMock()
        mock_conv.summary = ""
        self.mock_chat_repo.get_conversation_with_documents.return_value = mock_conv

        self.mock_rag_chain.generate_conversation_summary_async.return_value = (
            "Người dùng đã hỏi về Luật Doanh nghiệp 2020 và AI đã giải đáp."
        )

        result = await self.service.trigger_summarization_if_needed(conversation_id=1, user_id=10)

        self.assertIsNotNone(result)
        self.assertEqual(result, "Người dùng đã hỏi về Luật Doanh nghiệp 2020 và AI đã giải đáp.")
        self.mock_chat_repo.update_conversation_summary.assert_called_once_with(
            1, 10, "Người dùng đã hỏi về Luật Doanh nghiệp 2020 và AI đã giải đáp."
        )

    async def test_tenant_isolation_on_summary_update(self):
        # Đảm bảo User A không thể update summary của User B
        self.mock_chat_repo.count_messages_for_user.return_value = 15
        self.mock_chat_repo.get_messages_before_recent_for_user.return_value = [MagicMock(role="user", content="Test")]
        self.mock_chat_repo.get_conversation_with_documents.return_value = None

        result = await self.service.trigger_summarization_if_needed(conversation_id=1, user_id=999)

        self.assertIsNone(result)
        self.mock_chat_repo.update_conversation_summary.assert_not_called()


class TestRedisAndCeleryConfig(unittest.TestCase):
    def test_redis_url_setting_configured(self):
        from core.config import settings
        self.assertTrue(settings.REDIS_URL.startswith("redis://") or settings.REDIS_URL.startswith("rediss://"))

    def test_celery_broker_configured_with_redis(self):
        from core.celery_app import celery_app
        broker_url = celery_app.conf.broker_url
        self.assertTrue(broker_url.startswith("redis://") or broker_url.startswith("rediss://"))
        self.assertTrue(celery_app.conf.result_backend.startswith("redis://") or celery_app.conf.result_backend.startswith("rediss://"))


if __name__ == "__main__":
    unittest.main()
