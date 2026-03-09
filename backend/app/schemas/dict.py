from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DictTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class DictTypeCreate(DictTypeBase):
    pass


class DictTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DictTypeResponse(DictTypeBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DictItemBase(BaseModel):
    type_id: int
    code: str
    name: str
    sort_order: int = 0
    is_default: bool = False


class DictItemCreate(DictItemBase):
    pass


class DictItemUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    sort_order: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class DictItemResponse(DictItemBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
