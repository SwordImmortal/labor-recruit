from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.models.user import User
from app.models.candidate import Candidate, CandidateStatus
from app.models.onboarding import Onboarding, OnboardingStatus
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取工作台统计数据"""
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    # 今日线索数
    today_leads_query = select(func.count(Candidate.id)).where(
        func.date(Candidate.created_at) == today
    )
    if current_user.role.value == "recruiter":
        today_leads_query = today_leads_query.where(Candidate.owner_id == current_user.id)
    today_leads_result = await db.execute(today_leads_query)
    today_leads = today_leads_result.scalar() or 0
    
    # 待跟进数（超过24小时未跟进的线索/加微信状态）
    pending_follow_query = select(func.count(Candidate.id)).where(
        Candidate.status.in_([CandidateStatus.LEAD, CandidateStatus.WECHAT])
    )
    if current_user.role.value == "recruiter":
        pending_follow_query = pending_follow_query.where(Candidate.owner_id == current_user.id)
    pending_follow_result = await db.execute(pending_follow_query)
    pending_follow = pending_follow_result.scalar() or 0
    
    # 本月入职数
    month_onboard_query = select(func.count(Onboarding.id)).where(
        func.date(Onboarding.onboard_date) >= month_start
    )
    if current_user.role.value == "recruiter":
        month_onboard_query = month_onboard_query.where(Onboarding.owner_id == current_user.id)
    month_onboard_result = await db.execute(month_onboard_query)
    month_onboard = month_onboard_result.scalar() or 0
    
    # 当前在职人数
    current_online_query = select(func.count(Onboarding.id)).where(
        Onboarding.status == OnboardingStatus.ONLINE
    )
    if current_user.role.value == "recruiter":
        current_online_query = current_online_query.where(Onboarding.owner_id == current_user.id)
    current_online_result = await db.execute(current_online_query)
    current_online = current_online_result.scalar() or 0
    
    return {
        "today_leads": today_leads,
        "pending_follow": pending_follow,
        "month_onboard": month_onboard,
        "current_online": current_online
    }


@router.get("/recent-candidates")
async def get_recent_candidates(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取最近候选人"""
    query = select(Candidate)
    
    if current_user.role.value == "recruiter":
        query = query.where(Candidate.owner_id == current_user.id)
    
    query = query.order_by(Candidate.created_at.desc()).limit(limit)
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    return candidates
