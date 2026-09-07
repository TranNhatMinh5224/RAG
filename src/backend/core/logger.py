import json
import logging
import os
import sys
import contextvars
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

# Context variables để lưu trữ request_id và user_id cho từng luồng xử lý
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_ctx: contextvars.ContextVar[int | None] = contextvars.ContextVar("user_id", default=None)


def get_request_id() -> str | None:
    return request_id_ctx.get()


def set_request_id(req_id: str | None):
    request_id_ctx.set(req_id)


def get_user_id() -> int | None:
    return user_id_ctx.get()


def set_user_id(uid: int | None):
    user_id_ctx.set(uid)


class CustomJSONFormatter(logging.Formatter):
    """
    Formatter chuẩn hóa log thành JSON tương thích trực tiếp với AWS CloudWatch Logs,
    Datadog và ELK Stack.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or get_request_id(),
            "user_id": getattr(record, "user_id", None) or get_user_id(),
        }

        # Bổ sung thông tin ngoại lệ nếu có lỗi
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Bổ sung các trường tùy chọn truyền vào qua extra={}
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "request_id", "user_id"
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Khởi tạo hệ thống Structured Logging:
    - Stdout: JSON cho AWS CloudWatch / Docker driver.
    - File: logs/app.log tự động xoay vòng (Rotating: tối đa 10MB, lưu 5 bản sao).
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    formatter = CustomJSONFormatter()

    # 1. Handler xuất ra stdout (AWS CloudWatch thu thập tự nhiên)
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(numeric_level)

    # 2. Handler ghi file quay vòng (Bảo vệ ổ đĩa máy chủ không bị tràn)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)

    # Cấu hình Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers = [stdout_handler, file_handler]

    # Giảm nhiễu từ các thư viện bên thứ 3
    logging.getLogger("uvicorn.access").handlers = [stdout_handler, file_handler]
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Hàm tiện ích lấy logger theo tên module"""
    return logging.getLogger(name)
