import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from core.logger import set_request_id, set_user_id, get_logger

logger = get_logger("core.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware gắn X-Request-ID cho mỗi lượt gọi API và ghi log có cấu trúc:
    - Nhận diện hoặc tạo mới Request ID.
    - Đo thời gian xử lý (duration_ms).
    - Trả lại X-Request-ID ở Response Headers.
    - Bắt lỗi ngoại lệ không kiểm soát được và log kèm stacktrace.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Lấy Request ID từ client/ALB nếu có, hoặc tạo mới
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = f"req-{uuid.uuid4().hex[:12]}"

        set_request_id(request_id)
        set_user_id(None)

        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"

        # Bỏ qua log spam đối với health check
        if request.url.path != "/":
            logger.info(
                f"Bắt đầu xử lý {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                }
            )

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Gắn Request ID vào Header trả về cho client
            response.headers["X-Request-ID"] = request_id

            if request.url.path != "/":
                logger.info(
                    f"Hoàn tất {request.method} {request.url.path} - {response.status_code} ({duration_ms}ms)",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                    }
                )

            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                f"Lỗi không mong muốn tại {request.method} {request.url.path}: {str(exc)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Đã xảy ra lỗi hệ thống. Vui lòng liên hệ quản trị viên kèm mã Request ID.",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id}
            )
        finally:
            set_request_id(None)
            set_user_id(None)
