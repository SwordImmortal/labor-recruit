from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.onboarding import Onboarding, OnboardingStatus, Resignation
from app.schemas.onboarding import OnboardingCreate, OnboardingUpdate, OnboardingResponse
from app.api.auth import get_current_user

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
    query = select(Onboarding)
    
    if status:
        query = query.where(Onboarding.status == status)
    if project_id:
        query = query.where(Onboarding.project_id == project_id)
    
    # 数据权限
    if current_user.role == UserRole.RECRUITER:
        query = query.where(Onboarding.owner_id == current_user.id)
    
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
    result = await db.execute(select(Onboarding).where(Onboarding.id == onboarding_id))
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")
    return onboarding


@router.post("", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding(
    onboarding_data: OnboardingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建入职记录"""
    if current_user.role == UserRole.RECRUITER:
        raise HTTPException(status_code=403, detail="权限不足")
    
    from app.models.candidate import Candidate, CandidateStatus
    
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
    return onboarding


@router.put("/{onboarding_id}", response_model=OnboardingResponse)
async def update_onboarding(
    onboarding_id: int,
    onboarding_data: OnboardingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新入职记录"""
    if current_user.role == UserRole.RECRUITER:
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = await db.execute(select(Onboarding).where(Onboarding.id == onboarding_id))
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")
    
    update_data = onboarding_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(onboarding, field, value)
    
    await db.commit()
    await db.refresh(onboarding)
    return onboarding


@router.post("/{onboarding_id}/resign")
async def add_resignation(
    onboarding_id: int,
    resign_date: str,
    reason: str,
    reason_detail: Optional[str] = None,
    need_replace: Optional[bool] = None,
    no_replace_reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加离职记录"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    from datetime import datetime
    from app.models.onboarding import ResignReason
    
    result = await db.execute(select(Onboarding).where(Onboarding.id == onboarding_id))
    onboarding = result.scalar_one_or_none()
    if not onboarding:
        raise HTTPException(status_code=404, detail="入职记录不存在")
    
    # 创建离职记录
    resignation = Resignation(
        onboarding_id=onboarding_id,
        resign_date=datetime.strptime(resign_date, "%Y-%m-%d").date(),
        reason=reason,
        reason_detail=reason_detail,
        need_replace=need_replace,
        no_replace_reason=no_replace_reason
    )
    db.add(resignation)
    
    # 更新入职状态
    onboarding.status = OnboardingStatus.OFFLINE
    
    await db.commit()
    return {"message": "离职记录已添加"}
