from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.project import BusinessType, RecruitStatus, OperationStatus, OnboardCriteria


class ProjectBase(BaseModel):
    name: str
    customer_id: Optional[int] = None
    business_type: BusinessType = BusinessType.RPO
    city: str
    target_count: int = 0
    start_date: date
    end_date: Optional[date] = None
    recruit_status: RecruitStatus = RecruitStatus.PENDING
    operation_status: OperationStatus = OperationStatus.PENDING
    onboard_criteria: OnboardCriteria = OnboardCriteria.ONBOARD
    trial_days: int = 0
    need_training: bool = False
    need_buy_pack: bool = False
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    customer_id: Optional[int] = None
    business_type: Optional[BusinessType] = None
    city: Optional[str] = None
    target_count: Optional[int] = None
    current_count: Optional[int] = None
    end_date: Optional[date] = None
    recruit_status: Optional[RecruitStatus] = None
    operation_status: Optional[OperationStatus] = None
    onboard_criteria: Optional[OnboardCriteria] = None
    trial_days: Optional[int] = None
    need_training: Optional[bool] = None
    need_buy_pack: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    current_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
