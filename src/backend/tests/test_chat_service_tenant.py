import unittest
from datetime import datetime
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.chat_service import ChatService


class FakeChatRepository:
    def __init__(self):
        self.conversations = {}
        self.messages = {}
        self.saved_messages = []
        self.updated_documents = None

    async def get_conversation_with_documents(self, conversation_id, user_id):
        conversation = self.conversations.get(conversation_id)
        if conversation is None or conversation.user_id != user_id:
            return None
        return conversation

    async def get_recent_messages_for_user(self, conversation_id, user_id, limit=5):
        conversation = await self.get_conversation_with_documents(conversation_id, user_id)
        if conversation is None:
            return []
        return self.messages.get(conversation_id, [])[-limit:]

    async def set_documents_for_conversation(self, conversation_id, document_ids):
        self.updated_documents = (conversation_id, document_ids)

    async def add_message(self, message):
        self.saved_messages.append(message)
        return message


class FakeDocumentRepository:
    def __init__(self):
        self.documents = {}

    async def get_by_ids_and_user(self, document_ids, user_id):
        return [
            document
            for document_id in document_ids
            if (document := self.documents.get(document_id)) and document.user_id == user_id
        ]


class FakeRagChain:
    def __init__(self):
        self.calls = []

    async def answer_question_async(self, **kwargs):
        self.calls.append(kwargs)
        return "answer"


class ChatServiceTenantTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.chat_repo = FakeChatRepository()
        self.doc_repo = FakeDocumentRepository()
        self.rag_chain = FakeRagChain()
        self.service = ChatService(self.chat_repo, self.doc_repo, self.rag_chain)

        self.owned_document = SimpleNamespace(id=10, user_id=1)
        self.other_document = SimpleNamespace(id=20, user_id=2)
        self.doc_repo.documents = {
            self.owned_document.id: self.owned_document,
            self.other_document.id: self.other_document,
        }

        self.chat_repo.conversations = {
            100: SimpleNamespace(
                id=100,
                user_id=1,
                title="Owned",
                created_at=datetime(2026, 1, 1),
                documents=[self.owned_document],
            )
        }
        self.chat_repo.messages = {
            100: [
                SimpleNamespace(role="user", content="hello"),
                SimpleNamespace(role="ai", content="hi"),
            ]
        }

    async def test_attach_documents_returns_none_for_other_user_conversation(self):
        result = await self.service.attach_documents(
            user_id=2,
            conversation_id=100,
            document_ids=[20],
        )

        self.assertIsNone(result)
        self.assertIsNone(self.chat_repo.updated_documents)

    async def test_attach_documents_filters_documents_by_current_user(self):
        result = await self.service.attach_documents(
            user_id=1,
            conversation_id=100,
            document_ids=[10, 20],
        )

        self.assertEqual(result, 1)
        self.assertEqual(self.chat_repo.updated_documents, (100, [10]))

    async def test_get_conversation_details_returns_none_for_other_user(self):
        result = await self.service.get_conversation_details(
            user_id=2,
            conversation_id=100,
        )

        self.assertIsNone(result)

    async def test_prepare_chat_context_is_scoped_to_current_user(self):
        context = await self.service.prepare_chat_context(
            user_id=1,
            conversation_id=100,
        )
        denied_context = await self.service.prepare_chat_context(
            user_id=2,
            conversation_id=100,
        )

        self.assertEqual(context[0], [10])
        self.assertIn("hello", context[1])
        self.assertIsNone(denied_context)

    async def test_chat_with_document_rejects_other_user_before_rag_or_save(self):
        from services.exceptions import ConversationNotFoundError

        with self.assertRaises(ConversationNotFoundError):
            await self.service.chat_with_document(
                user_id=2,
                conversation_id=100,
                question="question",
            )

        self.assertEqual(self.rag_chain.calls, [])
        self.assertEqual(self.chat_repo.saved_messages, [])

    async def test_chat_with_document_runs_full_flow_for_owner(self):
        answer = await self.service.chat_with_document(
            user_id=1,
            conversation_id=100,
            question="question",
        )

        self.assertEqual(answer, "answer")
        self.assertEqual(len(self.rag_chain.calls), 1)
        self.assertEqual(self.rag_chain.calls[0]["document_ids"], [10])
        self.assertEqual([message.role for message in self.chat_repo.saved_messages], ["user", "ai"])
        self.assertEqual(self.chat_repo.saved_messages[0].content, "question")
        self.assertEqual(self.chat_repo.saved_messages[1].content, "answer")


if __name__ == "__main__":
    unittest.main()
