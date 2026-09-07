from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.activity_log import ActivityLog


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_activity(self, activity: ActivityLog) -> ActivityLog:
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def get_user_activities(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_activities_by_action(
        self,
        user_id: int,
        action: str,
        limit: int = 50,
    ) -> list[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .filter(ActivityLog.user_id == user_id, ActivityLog.action == action)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
