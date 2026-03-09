from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.channel import DictType, DictItem
from app.schemas.dict import DictTypeCreate, DictTypeUpdate, DictItemCreate, DictItemUpdate, DictTypeResponse, DictItemResponse
from app.api.auth import get_current_user

router = APIRouter()


# ============ 字典类型 ============

@router.get("/types", response_model=List[DictTypeResponse])
async def get_dict_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取字典类型列表"""
    result = await db.execute(select(DictType).order_by(DictType.created_at))
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


@router.put("/types/{type_id}", response_model=DictTypeResponse)
async def update_dict_type(
    type_id: int,
    data: DictTypeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新字典类型"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = await db.execute(select(DictType).where(DictType.id == type_id))
    dict_type = result.scalar_one_or_none()
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dict_type, field, value)
    
    await db.commit()
    await db.refresh(dict_type)
    return dict_type


# ============ 字典项 ============

@router.get("/items", response_model=List[DictItemResponse])
async def get_all_dict_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有字典项"""
    result = await db.execute(
        select(DictItem).order_by(DictItem.type_id, DictItem.sort_order)
    )
    return result.scalars().all()


@router.get("/types/{type_code}/items", response_model=List[DictItemResponse])
async def get_dict_items_by_type(
    type_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定类型的字典项"""
    result = await db.execute(
        select(DictItem)
        .join(DictType)
        .where(DictType.code == type_code)
        .where(DictItem.is_active == True)
        .order_by(DictItem.sort_order)
    )
    return result.scalars().all()


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


@router.put("/items/{item_id}", response_model=DictItemResponse)
async def update_dict_item(
    item_id: int,
    data: DictItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新字典项"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = await db.execute(select(DictItem).where(DictItem.id == item_id))
    dict_item = result.scalar_one_or_none()
    if not dict_item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dict_item, field, value)
    
    await db.commit()
    await db.refresh(dict_item)
    return dict_item
