from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OnboardingStatus(str, enum.Enum):
    """入职状态"""
    PENDING = "pending"      # 待上线
    ONLINE = "online"        # 在职
    OFFLINE = "offline"      # 已离职


class ResignReason(str, enum.Enum):
    """离职原因"""
    VOLUNTARY = "voluntary"   # 主动离职
    INVOLUNTARY = "involuntary"  # 被动离职
    OTHER = "other"          # 其他


class Onboarding(Base):
    """入职登记表"""
    __tablename__ = "onboardings"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, comment="候选人ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="入职项目ID")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="归属人ID")
    
    # 入职信息
    city = Column(String(50), nullable=False, comment="入职城市")
    id_card = Column(String(18), nullable=True, comment="身份证号")
    buy_pack_date = Column(Date, nullable=True, comment="购包日期")
    onboard_date = Column(Date, nullable=False, comment="入职日期")
    online_date = Column(Date, nullable=True, comment="上线日期")
    
    # 状态
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.PENDING, nullable=False, comment="状态")
    
    # 备注
    note = Column(Text, nullable=True, comment="备注")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    candidate = relationship("Candidate", back_populates="onboarding")
    project = relationship("Project", back_populates="onboardings")
    owner = relationship("User", back_populates="onboardings")
    resignations = relationship("Resignation", back_populates="onboarding", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Onboarding {self.id}>"


class Resignation(Base):
    """离职登记表"""
    __tablename__ = "resignations"

    id = Column(Integer, primary_key=True, index=True)
    onboarding_id = Column(Integer, ForeignKey("onboardings.id"), nullable=False, comment="入职记录ID")
    
    # 离职信息
    resign_date = Column(Date, nullable=False, comment="离职日期")
    reason = Column(Enum(ResignReason), nullable=False, comment="离职原因")
    reason_detail = Column(String(255), nullable=True, comment="离职原因详情")
    
    # 补招决策
    need_replace = Column(Boolean, nullable=True, comment="是否需要补招")
    no_replace_reason = Column(String(255), nullable=True, comment="不补招原因")
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    onboarding = relationship("Onboarding", back_populates="resignations")

    def __repr__(self):
        return f"<Resignation {self.id}>"
