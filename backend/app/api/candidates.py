from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.candidate import Candidate, CandidateStatus, FollowRecord
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.api.auth import get_current_user

router = APIRouter()


# ==================== 线索池相关 API ====================

@router.get("/leads/pool")
async def get_lead_pool(
    pool_type: str = Query("public", description="public=公海, mine=我的"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    channel_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取线索池列表"""
    query = select(Candidate).where(Candidate.status == CandidateStatus.LEAD)
    
    # 公海/我的筛选
    if pool_type == "public":
        query = query.where(Candidate.owner_id.is_(None))
    elif pool_type == "mine":
        query = query.where(Candidate.owner_id == current_user.id)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Candidate.name.contains(keyword),
                Candidate.phone.contains(keyword)
            )
        )
    
    # 渠道筛选
    if channel_id:
        query = query.where(Candidate.channel_id == channel_id)
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Candidate.created_at.desc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.post("/leads/{candidate_id}/claim")
async def claim_lead(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """领取线索（从公海领取到个人）"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    if candidate.status != CandidateStatus.LEAD:
        raise HTTPException(status_code=400, detail="该候选人不是线索状态")
    
    if candidate.owner_id is not None:
        raise HTTPException(status_code=400, detail="该线索已被领取")
    
    # 领取
    candidate.owner_id = current_user.id
    
    # 添加跟进记录
    follow = FollowRecord(
        candidate_id=candidate_id,
        operator_id=current_user.id,
        status_from="lead",
        status_to="lead",
        content="从公海领取线索",
        follow_at=datetime.now()
    )
    db.add(follow)
    
    await db.commit()
    return {"message": "领取成功"}


@router.post("/leads/{candidate_id}/assign")
async def assign_lead(
    candidate_id: int,
    owner_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """分配线索（管理员分配给招聘专员）"""
    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="无权分配线索")
    
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="线索不存在")
    
    # 检查目标用户是否存在
    user_result = await db.execute(select(User).where(User.id == owner_id))
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")
    
    # 分配
    candidate.owner_id = owner_id
    
    # 添加跟进记录
    follow = FollowRecord(
        candidate_id=candidate_id,
        operator_id=current_user.id,
        status_from="lead",
        status_to="lead",
        content=f"线索分配给 {target_user.real_name or target_user.username}",
        follow_at=datetime.now()
    )
    db.add(follow)
    
    await db.commit()
    return {"message": "分配成功"}


@router.post("/leads/batch-claim")
async def batch_claim_leads(
    candidate_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批量领取线索"""
    success_count = 0
    failed_items = []
    
    for cid in candidate_ids:
        result = await db.execute(select(Candidate).where(Candidate.id == cid))
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            failed_items.append({"id": cid, "reason": "线索不存在"})
            continue
        
        if candidate.status != CandidateStatus.LEAD:
            failed_items.append({"id": cid, "reason": "不是线索状态"})
            continue
        
        if candidate.owner_id is not None:
            failed_items.append({"id": cid, "reason": "已被领取"})
            continue
        
        candidate.owner_id = current_user.id
        success_count += 1
    
    await db.commit()
    
    return {
        "success_count": success_count,
        "failed_count": len(failed_items),
        "failed_items": failed_items
    }


@router.post("/leads/import")
async def import_leads(
    leads: List[dict],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批量导入线索（带重复检测）"""
    success_count = 0
    failed_items = []
    
    for idx, lead in enumerate(leads):
        phone = lead.get("phone", "").strip()
        name = lead.get("name", "").strip()
        
        # 必填检查
        if not phone or not name:
            failed_items.append({
                "row": idx + 1,
                "name": name,
                "phone": phone,
                "reason": "姓名或手机号为空"
            })
            continue
        
        # 手机号格式检查
        if len(phone) != 11 or not phone.isdigit():
            failed_items.append({
                "row": idx + 1,
                "name": name,
                "phone": phone,
                "reason": "手机号格式不正确"
            })
            continue
        
        # 重复检测
        result = await db.execute(select(Candidate).where(Candidate.phone == phone))
        existing = result.scalar_one_or_none()
        if existing:
            failed_items.append({
                "row": idx + 1,
                "name": name,
                "phone": phone,
                "reason": f"手机号已存在，重复候选人：{existing.name}"
            })
            continue
        
        # 创建线索
        candidate = Candidate(
            name=name,
            phone=phone,
            wechat=lead.get("wechat"),
            age=lead.get("age"),
            channel_id=lead.get("channel_id"),
            project_id=lead.get("project_id"),
            position_name=lead.get("position_name"),
            note=lead.get("note"),
            status=CandidateStatus.LEAD,
            owner_id=current_user.id
        )
        db.add(candidate)
        success_count += 1
    
    await db.commit()
    
    return {
        "success_count": success_count,
        "failed_count": len(failed_items),
        "failed_items": failed_items
    }


# ==================== 人才库相关 API ====================

@router.get("/talents/pool")
async def get_talent_pool(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取人才库列表"""
    query = select(Candidate).where(Candidate.in_talent_pool == True)
    
    # 关键词搜索
    if keyword:
        query = query.where(
            or_(
                Candidate.name.contains(keyword),
                Candidate.phone.contains(keyword)
            )
        )
    
    # 标签筛选（JSON 字段查询，简单实现）
    # 实际项目中可能需要使用 JSON 函数
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Candidate.updated_at.desc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.post("/talents/{candidate_id}/activate")
async def activate_talent(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """激活人才（从人才库转为线索）"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="人才不存在")
    
    if not candidate.in_talent_pool:
        raise HTTPException(status_code=400, detail="该候选人不在人才库中")
    
    # 激活
    candidate.in_talent_pool = False
    candidate.status = CandidateStatus.LEAD
    candidate.owner_id = current_user.id
    
    # 添加跟进记录
    follow = FollowRecord(
        candidate_id=candidate_id,
        operator_id=current_user.id,
        status_from="talent_pool",
        status_to="lead",
        content="从人才库激活为线索",
        follow_at=datetime.now()
    )
    db.add(follow)
    
    await db.commit()
    return {"message": "激活成功"}


@router.post("/talents/{candidate_id}/tags")
async def update_talent_tags(
    candidate_id: int,
    tags: List[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新人才标签"""
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="人才不存在")
    
    candidate.tags = tags
    await db.commit()
    
    return {"message": "标签更新成功", "tags": tags}


# ==================== 候选人管理 API ====================


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
