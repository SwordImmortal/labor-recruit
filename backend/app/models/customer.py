from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """Customer table"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="customer name")
    contact = Column(String(50), nullable=True, comment="contact person")
    phone = Column(String(20), nullable=True, comment="contact phone")
    address = Column(String(255), nullable=True, comment="address")
    remark = Column(Text, nullable=True, comment="remark")
    is_active = Column(Boolean, default=True, comment="is active")
    created_at = Column(DateTime, server_default=func.now(), comment="created at")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="updated at")

    # relationships
    projects = relationship("Project", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name}>"
