from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.channel import ChannelType


class ChannelBase(BaseModel):
    name: str
    type: ChannelType
    account: Optional[str] = None
    description: Optional[str] = None


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ChannelType] = None
    account: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class ChannelResponse(ChannelBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
