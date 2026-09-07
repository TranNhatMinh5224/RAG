from models.activity_log import ActivityLog
from repositories.activity_repository import ActivityRepository
from core.logger import get_logger, get_request_id

logger = get_logger("services.activity_service")


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo

    async def record_activity(
        self,
        action: str,
        user_id: int | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
    ) -> ActivityLog | None:
        """
        Ghi nhận nhật ký hoạt động (Audit Trail).
        Bọc try-except toàn diện để lỗi ghi log không bao giờ làm gián đoạn nghiệp vụ chính.
        """
        try:
            req_id = request_id or get_request_id()
            activity = ActivityLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id is not None else None,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=req_id,
            )
            created = await self.activity_repo.add_activity(activity)
            logger.info(
                f"Audit: [{action}] bởi user_id={user_id} đối với {resource_type}={resource_id}",
                extra={
                    "audit_action": action,
                    "target_user_id": user_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                }
            )
            return created
        except Exception as e:
            logger.warning(f"⚠️ Không thể lưu Activity Log [{action}]: {e}")
            return None

    async def get_user_activities(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActivityLog]:
        return await self.activity_repo.get_user_activities(user_id=user_id, limit=limit, offset=offset)
