from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CandidateStatus(str, enum.Enum):
    """候选人状态"""
    LEAD = "lead"              # 线索
    WECHAT = "wechat"          # 已加微信
    INTERVIEW = "interview"    # 已约面
    INTERVIEWED = "interviewed"  # 已到面
    ONBOARDED = "onboarded"    # 已入职
    LOST = "lost"              # 流失


class Candidate(Base):
    """候选人表"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(11), nullable=False, index=True, comment="手机号")
    wechat = Column(String(50), nullable=True, index=True, comment="微信号")
    age = Column(Integer, nullable=True, comment="年龄")
    
    # 渠道和项目
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True, comment="渠道ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, comment="应聘项目ID")
    position_name = Column(String(50), nullable=True, comment="应聘岗位")
    
    # 归属关系
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="邀约人ID")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="跟进人ID，为空表示公海线索")
    
    # 状态
    status = Column(Enum(CandidateStatus), default=CandidateStatus.LEAD, nullable=False, comment="状态")
    
    # 人才库
    in_talent_pool = Column(Boolean, default=False, comment="是否在人才库")
    tags = Column(JSON, nullable=True, comment="标签列表")
    
    # 面试信息
    interview_time = Column(DateTime, nullable=True, comment="面试时间")
    interview_feedback = Column(String(255), nullable=True, comment="面试反馈")
    
    # 备注
    note = Column(Text, nullable=True, comment="备注")
    
    # 重复标记
    is_duplicate = Column(Boolean, default=False, comment="是否重复")
    duplicate_reason = Column(String(255), nullable=True, comment="重复原因")
    
    # 时间
    last_follow_at = Column(DateTime, nullable=True, comment="最后跟进时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    channel = relationship("Channel", back_populates="candidates")
    project = relationship("Project", back_populates="candidates")
    inviter = relationship("User", foreign_keys=[inviter_id], backref="invited_candidates")
    owner = relationship("User", back_populates="candidates", foreign_keys=[owner_id])
    follow_records = relationship("FollowRecord", back_populates="candidate", cascade="all, delete-orphan")
    onboarding = relationship("Onboarding", back_populates="candidate", uselist=False)

    def __repr__(self):
        return f"<Candidate {self.name}>"


class FollowRecord(Base):
    """跟进记录表"""
    __tablename__ = "follow_records"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, comment="候选人ID")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    
    # 状态变更
    status_from = Column(String(50), nullable=True, comment="原状态")
    status_to = Column(String(50), nullable=True, comment="新状态")
    
    # 跟进内容
    content = Column(Text, nullable=True, comment="跟进内容")
    
    # 时间
    follow_at = Column(DateTime, nullable=False, comment="跟进时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    candidate = relationship("Candidate", back_populates="follow_records")
    operator = relationship("User", backref="follow_records")

    def __repr__(self):
        return f"<FollowRecord {self.id}>"
