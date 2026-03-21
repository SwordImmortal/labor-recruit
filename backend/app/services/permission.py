from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole


class PermissionService:
    """数据权限服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_accessible_user_ids(self, current_user: User) -> List[int]:
        """
        获取当前用户可访问的用户ID列表
        - admin: 全部用户
        - supervisor: 自己 + 下属
        - recruiter: 仅自己
        """
        if current_user.role == UserRole.ADMIN:
            # 管理员：获取所有用户
            result = await self.db.execute(select(User.id))
            return [row[0] for row in result.all()]

        elif current_user.role == UserRole.SUPERVISOR:
            # 主管：自己 + 下属
            user_ids = [current_user.id]

            # 获取下属专员
            result = await self.db.execute(
                select(User.id).where(User.parent_id == current_user.id)
            )
            user_ids.extend([row[0] for row in result.all()])

            return user_ids

        else:
            # 专员：仅自己
            return [current_user.id]

    async def filter_by_owner(self, current_user: User, owner_field_name: str = "owner_id"):
        """
        获取数据过滤条件
        返回可访问的 owner_id 列表
        """
        return await self.get_accessible_user_ids(current_user)
