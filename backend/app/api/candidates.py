from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.candidate import Candidate, CandidateStatus
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[CandidateResponse])
async def get_candidates(
    skip: int = 0,
    limit: int = 20,
    status: Optional[CandidateStatus] = None,
    project_id: Optional[int] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取候选人列表"""
    query = select(Candidate)
    
    # 数据权限
    if current_user.role == UserRole.RECRUITER:
        query = query.where(Candidate.owner_id == current_user.id)
    
    # 筛选条件
    if status:
        query = query.where(Candidate.status == status)
    if project_id:
        query = query.where(Candidate.project_id == project_id)
    if keyword:
        query = query.where(
            or_(
                Candidate.name.contains(keyword),
                Candidate.phone.contains(keyword),
                Candidate.wechat.contains(keyword)
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(Candidate.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取候选人详情"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 数据权限检查
    if current_user.role == UserRole.RECRUITER and candidate.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看")
    
    return candidate


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建候选人"""
    # 检查手机号是否重复
    result = await db.execute(select(Candidate).where(Candidate.phone == candidate_data.phone))
    existing = result.scalar_one_or_none()
    if existing:
        # 标记为重复
        candidate = Candidate(
            **candidate_data.dict(),
            owner_id=current_user.id,
            is_duplicate=True,
            duplicate_reason="手机号已存在"
        )
    else:
        candidate = Candidate(
            **candidate_data.dict(),
            owner_id=current_user.id
        )
    
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新候选人"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 权限检查
    if current_user.role == UserRole.RECRUITER and candidate.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改")
    
    update_data = candidate_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}/follows")
async def get_follow_records(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取候选人跟进记录"""
    from app.models.candidate import FollowRecord
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 数据权限检查
    if current_user.role == UserRole.RECRUITER and candidate.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看")
    
    # 获取跟进记录
    query = select(FollowRecord).where(
        FollowRecord.candidate_id == candidate_id
    ).options(
        selectinload(FollowRecord.operator)
    ).order_by(FollowRecord.follow_at.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # 转换为可序列化格式
    return [
        {
            "id": r.id,
            "status_from": r.status_from,
            "status_to": r.status_to,
            "content": r.content,
            "follow_at": r.follow_at.strftime("%Y-%m-%d %H:%M") if r.follow_at else None,
            "operator_name": r.operator.real_name or r.operator.username if r.operator else None
        }
        for r in records
    ]


@router.post("/{candidate_id}/follow")
async def add_follow_record(
    candidate_id: int,
    content: str,
    status_to: Optional[CandidateStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加跟进记录"""
    from app.models.candidate import FollowRecord
    from datetime import datetime
    
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    
    # 创建跟进记录
    follow = FollowRecord(
        candidate_id=candidate_id,
        operator_id=current_user.id,
        status_from=candidate.status.value if candidate.status else None,
        status_to=status_to.value if status_to else None,
        content=content,
        follow_at=datetime.now()
    )
    db.add(follow)
    
    # 更新候选人状态
    if status_to:
        candidate.status = status_to
    candidate.last_follow_at = datetime.now()
    
    await db.commit()
    return {"message": "跟进记录已添加"}
