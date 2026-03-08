from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.onboarding import OnboardingStatus


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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
