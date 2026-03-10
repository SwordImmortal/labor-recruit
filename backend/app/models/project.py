# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BusinessType(str, enum.Enum):
    """Business Type"""
    RPO = "rpo"
    BPO = "bpo"


class RecruitStatus(str, enum.Enum):
    """Recruit Status"""
    PENDING = "pending"
    RECRUITING = "recruiting"
    FILLED = "filled"
    REPLACING = "replacing"
    STOPPED = "stopped"


class OperationStatus(str, enum.Enum):
    """Operation Status"""
    PENDING = "pending"
    SERVING = "serving"
    PAUSED = "paused"
    TERMINATED = "terminated"


class OnboardCriteria(str, enum.Enum):
    """Onboard Criteria"""
    ONBOARD = "onboard"
    BUY_PACK = "buy_pack"


class Project(Base):
    """Project table"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    business_type = Column(Enum(BusinessType), default=BusinessType.RPO, nullable=False)
    city = Column(String(50), nullable=False)
    target_count = Column(Integer, default=0)
    current_count = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    recruit_status = Column(Enum(RecruitStatus), default=RecruitStatus.PENDING)
    operation_status = Column(Enum(OperationStatus), default=OperationStatus.PENDING)
    onboard_criteria = Column(Enum(OnboardCriteria), default=OnboardCriteria.ONBOARD)
    trial_days = Column(Integer, default=0)
    need_training = Column(Boolean, default=False)
    need_buy_pack = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # relationships
    customer = relationship("Customer", back_populates="projects")
    owner = relationship("User", backref="projects")
    positions = relationship("ProjectPosition", back_populates="project", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="project")
    onboardings = relationship("Onboarding", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"


class ProjectPosition(Base):
    """Project Position table"""
    __tablename__ = "project_positions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    position_name = Column(String(50), nullable=False)
    target_count = Column(Integer, default=0)
    current_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    project = relationship("Project", back_populates="positions")

    def __repr__(self):
        return f"<ProjectPosition {self.position_name}>"
