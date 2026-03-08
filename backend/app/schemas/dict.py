from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DictTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class DictTypeCreate(DictTypeBase):
    pass


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


class DictItemResponse(DictItemBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
