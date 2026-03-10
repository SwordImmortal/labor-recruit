from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models import User
from app.models.customer import Customer
from app.models.project import Project
from app.models.candidate import Candidate, CandidateStatus
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.schemas.customer import CustomerStatResponse

router = APIRouter(prefix="/customers", tags=["客户管理"])


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取客户列表"""
    query = select(Customer)
    
    # 搜索
    if keyword:
        query = query.where(
            or_(
                Customer.name.contains(keyword),
                Customer.contact.contains(keyword),
                Customer.phone.contains(keyword)
            )
        )
    
    # 筛选
    if is_active is not None:
        query = query.where(Customer.is_active == is_active)
    
    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Customer.created_at.desc())
    result = await db.execute(query)
    customers = result.scalars().all()
    
    return CustomerListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=customers
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取客户详情"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@router.get("/{customer_id}/stats", response_model=CustomerStatResponse)
async def get_customer_stats(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取客户统计数据"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 统计项目数
    project_result = await db.execute(
        select(func.count()).where(Project.customer_id == customer_id)
    )
    project_count = project_result.scalar()
    
    # 统计活跃项目数
    active_result = await db.execute(
        select(func.count()).where(
            Project.customer_id == customer_id,
            Project.is_active == True
        )
    )
    active_project_count = active_result.scalar()
    
    # 统计入职人数（通过项目关联）
    onboarded_result = await db.execute(
        select(func.count()).select_from(Candidate).join(Project).where(
            Project.customer_id == customer_id,
            Candidate.status == CandidateStatus.ONBOARDED
        )
    )
    onboarded_count = onboarded_result.scalar()
    
    return CustomerStatResponse(
        customer_id=customer_id,
        project_count=project_count,
        active_project_count=active_project_count,
        onboarded_count=onboarded_count
    )


@router.post("", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建客户"""
    # 检查名称是否重复
    result = await db.execute(select(Customer).where(Customer.name == data.name))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="客户名称已存在")
    
    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新客户"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 检查名称是否重复
    if data.name and data.name != customer.name:
        existing = await db.execute(select(Customer).where(Customer.name == data.name))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="客户名称已存在")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    
    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除客户"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 检查是否有关联项目
    project_result = await db.execute(
        select(func.count()).where(Project.customer_id == customer_id)
    )
    project_count = project_result.scalar()
    if project_count > 0:
        raise HTTPException(status_code=400, detail=f"该客户下有 {project_count} 个项目，无法删除")
    
    await db.delete(customer)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/select/list")
async def get_customers_for_select(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取客户下拉列表（用于表单选择）"""
    result = await db.execute(
        select(Customer).where(Customer.is_active == True).order_by(Customer.name)
    )
    customers = result.scalars().all()
    
    return [
        {"id": c.id, "name": c.name}
        for c in customers
    ]
