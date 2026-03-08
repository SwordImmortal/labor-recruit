from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.candidate import CandidateStatus


class CandidateBase(BaseModel):
    name: str
    phone: str
    wechat: Optional[str] = None
    age: Optional[int] = None
    channel_id: Optional[int] = None
    project_id: Optional[int] = None
    position_name: Optional[str] = None
    inviter_id: Optional[int] = None
    note: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    age: Optional[int] = None
    channel_id: Optional[int] = None
    project_id: Optional[int] = None
    position_name: Optional[str] = None
    inviter_id: Optional[int] = None
    status: Optional[CandidateStatus] = None
    interview_time: Optional[datetime] = None
    interview_feedback: Optional[str] = None
    note: Optional[str] = None
    is_duplicate: Optional[bool] = None
    duplicate_reason: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: int
    owner_id: int
    status: CandidateStatus
    interview_time: Optional[datetime]
    interview_feedback: Optional[str]
    is_duplicate: bool
    duplicate_reason: Optional[str]
    last_follow_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
