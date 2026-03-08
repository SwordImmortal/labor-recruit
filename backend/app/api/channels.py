from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.channel import Channel
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[ChannelResponse])
async def get_channels(
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取渠道列表"""
    query = select(Channel)
    
    if is_active is not None:
        query = query.where(Channel.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(Channel.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建渠道"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    channel = Channel(**channel_data.dict())
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新渠道"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    
    update_data = channel_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)
    
    await db.commit()
    await db.refresh(channel)
    return channel
