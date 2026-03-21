from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.onboarding import Onboarding, OnboardingStatus, Resignation, ResignReason
from app.models.candidate import Candidate, CandidateStatus
from app.schemas.onboarding import OnboardingCreate, OnboardingUpdate, OnboardingResponse
from app.api.auth import get_current_user
from app.services.permission import PermissionService

router = APIRouter()


@router.get("", response_model=List[OnboardingResponse])
async def get_onboardings(
    skip: int = 0,
    limit: int = 20,
    status: Optional[OnboardingStatus] = None,
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取入职列表"""
    query = select(Onboarding).options(
        selectinload(Onboarding.candidate),
        selectinload(Onboarding.project)
    )
    
    if status:
        query = query.where(Onboarding.status == status)
    if project_id:
        query = query.where(Onboarding.project_id == project_id)
    
    # 数据权限 - 使用权限服务
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)
    query = query.where(Onboarding.owner_id.in_(accessible_user_ids))
    
    query = query.offset(skip).limit(limit).order_by(Onboarding.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{onboarding_id}", response_model=OnboardingResponse)
async def get_onboarding(
    onboarding_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取入职详情"""
    # 数据权限检查
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)

    query = select(Onboarding).options(
        selectinload(Onboarding.candidate),
        selectinload(Onboarding.project)
    ).where(Onboarding.id == onboarding_id)

    result = await db.execute(query)
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")

    # 检查权限
    if onboarding.owner_id not in accessible_user_ids:
        raise HTTPException(status_code=403, detail="无权限访问该记录")

    return onboarding


@router.post("", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding(
    onboarding_data: OnboardingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建入职记录"""
    # 检查候选人是否存在
    result = await db.execute(select(Candidate).where(Candidate.id == onboarding_data.candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 创建入职记录
    onboarding = Onboarding(
        **onboarding_data.dict(),
        owner_id=current_user.id
    )
    db.add(onboarding)
    
    # 更新候选人状态
    candidate.status = CandidateStatus.ONBOARDED
    
    await db.commit()
    await db.refresh(onboarding)
    
    # 重新加载关联
    query = select(Onboarding).options(
        selectinload(Onboarding.candidate),
        selectinload(Onboarding.project)
    ).where(Onboarding.id == onboarding.id)
    result = await db.execute(query)
    return result.scalar_one()


@router.put("/{onboarding_id}", response_model=OnboardingResponse)
async def update_onboarding(
    onboarding_id: int,
    onboarding_data: OnboardingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新入职记录"""
    # 数据权限检查
    permission_service = PermissionService(db)
    accessible_user_ids = await permission_service.get_accessible_user_ids(current_user)

    query = select(Onboarding).options(
        selectinload(Onboarding.candidate),
        selectinload(Onboarding.project)
    ).where(Onboarding.id == onboarding_id)

    result = await db.execute(query)
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")

    # 检查权限
    if onboarding.owner_id not in accessible_user_ids:
        raise HTTPException(status_code=403, detail="无权限修改该记录")

    update_data = onboarding_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(onboarding, field, value)

    await db.commit()
    await db.refresh(onboarding)

    # 重新加载关联
    query = select(Onboarding).options(
        selectinload(Onboarding.candidate),
        selectinload(Onboarding.project)
    ).where(Onboarding.id == onboarding.id)
    result = await db.execute(query)
    return result.scalar_one()


class ResignRequest(BaseModel):
    resign_date: str
    reason: str
    reason_detail: Optional[str] = None
    need_replace: Optional[bool] = None
    no_replace_reason: Optional[str] = None


@router.post("/{onboarding_id}/resign")
async def add_resignation(
    onboarding_id: int,
    resign_data: ResignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加离职记录"""
    result = await db.execute(select(Onboarding).where(Onboarding.id == onboarding_id))
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")
    
    # 创建离职记录
    resignation = Resignation(
        onboarding_id=onboarding_id,
        resign_date=datetime.strptime(resign_data.resign_date, "%Y-%m-%d").date(),
        reason=resign_data.reason,
        reason_detail=resign_data.reason_detail,
        need_replace=resign_data.need_replace,
        no_replace_reason=resign_data.no_replace_reason
    )
    db.add(resignation)
    
    # 更新入职状态
    onboarding.status = OnboardingStatus.OFFLINE
    
    await db.commit()
    return {"message": "离职记录已添加"}
