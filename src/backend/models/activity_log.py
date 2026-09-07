from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class ActivityLog(Base):
    """
    Nhật ký hoạt động (Audit Trail) phục vụ kiểm toán bảo mật,
    truy vết hành vi người dùng và tuân thủ tiêu chuẩn pháp lý.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # Ví dụ: USER_LOGIN, DOCUMENT_UPLOAD, DOCUMENT_DELETE, CHAT_QUERY
    resource_type = Column(String, nullable=True)        # document, conversation, user
    resource_id = Column(String, nullable=True)          # ID tài nguyên bị tác động
    details = Column(Text, nullable=True)                # Thông tin bổ sung
    ip_address = Column(String, nullable=True)           # Địa chỉ IP của client
    user_agent = Column(String, nullable=True)           # Trình duyệt / Ứng dụng client
    request_id = Column(String, nullable=True, index=True)  # Khóa liên kết với log hệ thống trên AWS CloudWatch
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ với người dùng
    user = relationship("User", backref="activity_logs")
