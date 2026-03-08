from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ChannelType(str, enum.Enum):
    """渠道类型"""
    BOSS = "boss"           # BOSS直聘
    KUAISHOU = "kuaishou"   # 快手
    WUBA = "wuba"           # 58同城
    DOUYIN = "douyin"       # 抖音
    OFFLINE = "offline"     # 线下


class Channel(Base):
    """渠道表"""
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="渠道名称")
    type = Column(Enum(ChannelType), nullable=False, comment="渠道类型")
    account = Column(String(100), nullable=True, comment="渠道账号")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(String(255), nullable=True, comment="描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    candidates = relationship("Candidate", back_populates="channel")

    def __repr__(self):
        return f"<Channel {self.name}>"


class DictType(Base):
    """字典类型表"""
    __tablename__ = "dict_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, comment="字典编码")
    name = Column(String(50), nullable=False, comment="字典名称")
    description = Column(String(255), nullable=True, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<DictType {self.code}>"


class DictItem(Base):
    """字典项表"""
    __tablename__ = "dict_items"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("dict_types.id"), nullable=False, comment="字典类型ID")
    code = Column(String(50), nullable=False, comment="字典项编码")
    name = Column(String(50), nullable=False, comment="字典项名称")
    sort_order = Column(Integer, default=0, comment="排序")
    is_default = Column(Boolean, default=False, comment="是否默认")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    type = relationship("DictType", backref="items")

    def __repr__(self):
        return f"<DictItem {self.code}>"
