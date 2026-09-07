import sys
import os
import json
import logging
import unittest
from unittest.mock import AsyncMock, MagicMock

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from core.logger import CustomJSONFormatter, set_request_id, get_request_id, set_user_id
from services.activity_service import ActivityService
from models.activity_log import ActivityLog


class TestCustomJSONFormatter(unittest.TestCase):
    def test_json_formatter_includes_required_fields(self):
        formatter = CustomJSONFormatter()
        set_request_id("req-test-12345")
        set_user_id(42)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=10,
            msg="Thông báo kiểm tra logging",
            args=(),
            exc_info=None,
        )
        record.duration_ms = 15.6

        formatted_output = formatter.format(record)
        log_obj = json.loads(formatted_output)

        self.assertEqual(log_obj["level"], "INFO")
        self.assertEqual(log_obj["logger"], "test_logger")
        self.assertEqual(log_obj["message"], "Thông báo kiểm tra logging")
        self.assertEqual(log_obj["request_id"], "req-test-12345")
        self.assertEqual(log_obj["user_id"], 42)
        self.assertEqual(log_obj["duration_ms"], 15.6)
        self.assertIn("timestamp", log_obj)

        set_request_id(None)
        set_user_id(None)


class TestActivityService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_repo = AsyncMock()
        self.activity_service = ActivityService(self.mock_repo)

    async def test_record_activity_success(self):
        set_request_id("req-audit-999")

        saved_log = ActivityLog(
            id=1,
            user_id=10,
            action="DOCUMENT_UPLOAD",
            resource_type="document",
            resource_id="101",
            details="Upload file test.pdf",
            request_id="req-audit-999",
        )
        self.mock_repo.add_activity.return_value = saved_log

        result = await self.activity_service.record_activity(
            action="DOCUMENT_UPLOAD",
            user_id=10,
            resource_type="document",
            resource_id="101",
            details="Upload file test.pdf",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.action, "DOCUMENT_UPLOAD")
        self.assertEqual(result.request_id, "req-audit-999")
        self.mock_repo.add_activity.assert_called_once()

        set_request_id(None)

    async def test_record_activity_safe_failure_never_crashes(self):
        # Đảm bảo nếu database lỗi khi ghi log, nghiệp vụ không bị crash
        self.mock_repo.add_activity.side_effect = Exception("Database connection lost")

        result = await self.activity_service.record_activity(
            action="DOCUMENT_DELETE",
            user_id=10,
            resource_type="document",
            resource_id="101",
        )

        self.assertIsNone(result)

    async def test_get_user_activities_calls_repo_with_user_id(self):
        mock_logs = [MagicMock(id=1, action="USER_LOGIN"), MagicMock(id=2, action="DOCUMENT_UPLOAD")]
        self.mock_repo.get_user_activities.return_value = mock_logs

        logs = await self.activity_service.get_user_activities(user_id=10, limit=20, offset=0)

        self.assertEqual(len(logs), 2)
        self.mock_repo.get_user_activities.assert_called_once_with(user_id=10, limit=20, offset=0)


if __name__ == "__main__":
    unittest.main()
