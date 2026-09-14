import re

# ==============================================================================
# BỘ QUY TẮC BẢO VỆ ĐẦU VÀO (INPUT SECURITY GUARDRAILS)
# ==============================================================================

GUARDRAIL_VIOLATION_PATTERNS = [
    # 1. Chống Prompt Injection & Jailbreak (DAN, Developer Mode, System Override)
    (
        r"(?i)(bỏ\s*qua|hủy\s*bỏ|quên\s*đi)\s+(tất\s*cả|mọi|hết)?\s*(các\s+)?(chỉ\s*dẫn|hướng\s*dẫn|quy\s*tắc|lệnh|câu\s*lệnh)\s*(trước|ban\s*đầu)?",
        "Prompt Injection bị chặn."
    ),
    (
        r"(?i)\b(ignore|disregard|forget)\s+(all\s+)?(previous\s+)?(instructions?|prompts?|rules?|commands?)\b",
        "Prompt Injection rejected."
    ),
    (
        r"(?i)\b(you are now|act as|hãy đóng vai|chuyển sang chế độ)\s+(in\s+)?(dan|jailbreak|developer mode|unrestricted|unfiltered|bất tuân)\b",
        "Jailbreak attempt rejected."
    ),
    (
        r"(?i)\b(system override|bypass security|bỏ qua bảo mật)\b",
        "System Override attempt rejected."
    ),
    # 2. Chống trích xuất System Prompt & Cấu hình nhạy cảm
    (
        r"(?i)(tiết\s*lộ|cho\s*xem|hiển\s*thị|in\s*ra|show|print|reveal|display)\s+(toàn\s*bộ\s+)?(system\s*prompt|câu\s*lệnh\s*hệ\s*thống|hướng\s*dẫn\s*hệ\s*thống|system\s*instructions?|prompt\s*gốc)",
        "Trích xuất System Prompt bị chặn."
    ),
    (
        r"(?i)(api[_\s-]?key|secret[_\s-]?key|database[_\s-]?url|mật\s*khẩu\s*database|db\s*password)",
        "Trích xuất thông tin bí mật hệ thống bị chặn."
    ),
]


def validate_user_input(question: str) -> tuple[bool, str]:
    """
    Kiểm tra an toàn câu hỏi của người dùng trước khi chuyển tiếp tới LLM (Pre-flight Guardrail).
    Trả về (is_safe: bool, refusal_message: str).
    """
    if not question:
        return True, ""

    for pattern, reason in GUARDRAIL_VIOLATION_PATTERNS:
        if re.search(pattern, question):
            return False, (
                "🛡️ **Cảnh Báo An Toàn Hệ Thống (Security Guardrail)**:\n\n"
                f"Yêu cầu của bạn đã bị từ chối do vi phạm chính sách bảo mật ({reason}).\n\n"
                "Hệ thống chỉ hỗ trợ tra cứu, phân tích và tóm tắt thông tin dựa trên các tài liệu nghiệp vụ đã được cấp quyền."
            )

    return True, ""
