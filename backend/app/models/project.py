from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BusinessType(str, enum.Enum):
    """业务类型"""
    RPO = "rpo"  # 招聘流程外包
    BPO = "bpo"  # 业务流程外包


class RecruitStatus(str, enum.Enum):
    """招聘状态"""
    PENDING = "pending"        # 待启动
    RECRUITING = "recruiting"  # 招聘中
    FILLED = "filled"          # 已招满
    REPLACING = "replacing"    # 补招中
    STOPPED = "stopped"        # 停招


class OperationStatus(str, enum.Enum):
    """运营状态"""
    PENDING = "pending"        # 待履约
    SERVING = "serving"        # 服务中
    PAUSED = "paused"          # 暂停服务
    TERMINATED = "terminated"  # 已终止


class OnboardCriteria(str, enum.Enum):
    """入职口径"""
    ONBOARD = "onboard"  # 入职
    BUY_PACK = "buy_pack"  # 购包


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="项目名称")
    business_type = Column(Enum(BusinessType), default=BusinessType.RPO, nullable=False, comment="业务类型")
    city = Column(String(50), nullable=False, comment="城市")
    target_count = Column(Integer, default=0, comment="目标人数")
    current_count = Column(Integer, default=0, comment="当前人数")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="负责人ID")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=True, comment="结束日期")
    recruit_status = Column(Enum(RecruitStatus), default=RecruitStatus.PENDING, comment="招聘状态")
    operation_status = Column(Enum(OperationStatus), default=OperationStatus.PENDING, comment="运营状态")
    onboard_criteria = Column(Enum(OnboardCriteria), default=OnboardCriteria.ONBOARD, comment="入职口径")
    trial_days = Column(Integer, default=0, comment="试单天数，0表示无")
    need_training = Column(Boolean, default=False, comment="是否需要培训")
    need_buy_pack = Column(Boolean, default=False, comment="是否需要购包")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="项目描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    owner = relationship("User", backref="projects")
    positions = relationship("ProjectPosition", back_populates="project", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="project")
    onboardings = relationship("Onboarding", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"


class ProjectPosition(Base):
    """项目岗位关联表"""
    __tablename__ = "project_positions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="项目ID")
    position_name = Column(String(50), nullable=False, comment="岗位名称")
    target_count = Column(Integer, default=0, comment="需求人数")
    current_count = Column(Integer, default=0, comment="当前人数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    project = relationship("Project", back_populates="positions")

    def __repr__(self):
        return f"<ProjectPosition {self.position_name}>"
