from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"           # 管理员
    SUPERVISOR = "supervisor" # 招聘主管
    RECRUITER = "recruiter"   # 招聘专员


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    phone = Column(String(11), unique=True, index=True, nullable=False, comment="手机号")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    role = Column(Enum(UserRole), default=UserRole.RECRUITER, nullable=False, comment="角色")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    candidates = relationship("Candidate", back_populates="owner", foreign_keys="Candidate.owner_id")
    onboardings = relationship("Onboarding", back_populates="owner")

    def __repr__(self):
        return f"<User {self.username}>"
