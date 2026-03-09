from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.onboarding import OnboardingStatus


class CandidateBrief(BaseModel):
    """候选人简要信息"""
    id: int
    name: str
    phone: str
    
    class Config:
        from_attributes = True


class ProjectBrief(BaseModel):
    """项目简要信息"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class OnboardingBase(BaseModel):
    candidate_id: int
    project_id: int
    city: str
    id_card: Optional[str] = None
    buy_pack_date: Optional[date] = None
    onboard_date: date
    online_date: Optional[date] = None
    note: Optional[str] = None


class OnboardingCreate(OnboardingBase):
    pass


class OnboardingUpdate(BaseModel):
    city: Optional[str] = None
    id_card: Optional[str] = None
    buy_pack_date: Optional[date] = None
    onboard_date: Optional[date] = None
    online_date: Optional[date] = None
    status: Optional[OnboardingStatus] = None
    note: Optional[str] = None


class OnboardingResponse(OnboardingBase):
    id: int
    owner_id: int
    status: OnboardingStatus
    candidate: Optional[CandidateBrief] = None
    project: Optional[ProjectBrief] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
