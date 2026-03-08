from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.channel import DictType, DictItem
from app.schemas.dict import DictTypeCreate, DictItemCreate, DictTypeResponse, DictItemResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/types", response_model=List[DictTypeResponse])
async def get_dict_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取字典类型列表"""
    result = await db.execute(select(DictType).where(DictType.is_active == True))
    return result.scalars().all()


@router.get("/types/{type_code}/items", response_model=List[DictItemResponse])
async def get_dict_items(
    type_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取字典项列表"""
    result = await db.execute(
        select(DictItem)
        .join(DictType)
        .where(DictType.code == type_code)
        .where(DictItem.is_active == True)
        .order_by(DictItem.sort_order)
    )
    return result.scalars().all()


@router.post("/types", response_model=DictTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_dict_type(
    data: DictTypeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建字典类型"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    dict_type = DictType(**data.dict())
    db.add(dict_type)
    await db.commit()
    await db.refresh(dict_type)
    return dict_type


@router.post("/items", response_model=DictItemResponse, status_code=status.HTTP_201_CREATED)
async def create_dict_item(
    data: DictItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建字典项"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    dict_item = DictItem(**data.dict())
    db.add(dict_item)
    await db.commit()
    await db.refresh(dict_item)
    return dict_item
