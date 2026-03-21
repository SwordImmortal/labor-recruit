from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.project import Project, RecruitStatus, OperationStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.auth import get_current_user
from app.services.permission import PermissionService

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 20,
    recruit_status: Optional[RecruitStatus] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目列表"""
    query = select(Project)

    # 数据权限 - 使用权限服务
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)
    query = query.where(Project.owner_id.in_(accessible_user_ids))

    if recruit_status:
        query = query.where(Project.recruit_status == recruit_status)
    if is_active is not None:
        query = query.where(Project.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 数据权限检查
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)
    if project.owner_id and project.owner_id not in accessible_user_ids:
        raise HTTPException(status_code=403, detail="无权查看")

    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建项目"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    project = Project(**project_data.dict(), owner_id=current_user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新项目"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 权限检查
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)
    if project.owner_id and project.owner_id not in accessible_user_ids:
        raise HTTPException(status_code=403, detail="无权修改")

    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除项目"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    project.is_active = False
    await db.commit()
    return {"message": "项目已禁用"}
