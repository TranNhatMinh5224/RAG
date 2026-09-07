from typing import List
from fastapi import APIRouter, Depends, Query
from api.dependencies import get_current_user, get_activity_service
from models.schemas import ActivityLogResponse
from models.user import User
from services.activity_service import ActivityService

router = APIRouter(
    prefix="/activity",
    tags=["Activity & Audit Logs"],
)


@router.get("/me", response_model=List[ActivityLogResponse])
async def get_my_activity_logs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    activity_service: ActivityService = Depends(get_activity_service),
):
    """Lấy danh sách nhật ký hoạt động của người dùng hiện tại (Multi-tenant)"""
    return await activity_service.get_user_activities(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
