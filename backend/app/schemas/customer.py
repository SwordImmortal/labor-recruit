from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """客户基础模型"""
    name: str = Field(..., max_length=100, description="客户名称")
    contact: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, max_length=255, description="地址")
    remark: Optional[str] = Field(None, description="备注")


class CustomerCreate(CustomerBase):
    """创建客户"""
    pass


class CustomerUpdate(BaseModel):
    """更新客户"""
    name: Optional[str] = Field(None, max_length=100, description="客户名称")
    contact: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, max_length=255, description="地址")
    remark: Optional[str] = Field(None, description="备注")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CustomerResponse(CustomerBase):
    """客户响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """客户列表响应"""
    total: int
    page: int
    page_size: int
    items: list[CustomerResponse]


class CustomerStatResponse(BaseModel):
    """客户统计响应"""
    customer_id: int
    project_count: int = Field(..., description="项目总数")
    active_project_count: int = Field(..., description="活跃项目数")
    onboarded_count: int = Field(..., description="入职人数")


class CustomerSelectItem(BaseModel):
    """客户下拉选项"""
    id: int
    name: str
