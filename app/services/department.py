from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, Department as DepartmentSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService
from .unit import get_unit_by_id

settings = get_settings()

# Create department pagination service
department_pagination = BasePaginationService[Department, DepartmentSchema](
    model=Department,
    schema=DepartmentSchema
)


async def get_department_by_id(db: AsyncSession, department_id: int) -> Optional[Department]:
    query = select(Department).where(
        Department.id == department_id,
        Department.deleted_at.is_(None)
    ).options(
        selectinload(Department.unit),
        selectinload(Department.parent)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_departments(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    unit_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
) -> PaginationResponse[DepartmentSchema]:
    """Get paginated list of departments"""
    # Initialize base query with joins
    query = (
        select(Department)
        .options(
            selectinload(Department.unit),
            selectinload(Department.parent)
        )
    )

    # Build where conditions
    conditions = []
    conditions.append(Department.deleted_at.is_(None))

    # Add filters
    filters = {
        "unit_id": unit_id,
        "parent_id": parent_id,
        "name": name,
        "code": code,
        "status": status
    }

    result = await department_pagination.get_paginated(
        db,
        page=page,
        size=size,
        query=query,
        **filters
    )

    return result


async def create_department(db: AsyncSession, department_data: DepartmentCreate) -> Department:
    # Check if unit exists
    unit = await get_unit_by_id(db, department_data.unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit does not exist"
        )

    # Check if parent department exists if provided
    if department_data.parent_id:
        parent = await get_department_by_id(db, department_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent department does not exist"
            )
        # Prevent circular reference during creation
        if parent.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent department is inactive"
            )

    # Check code uniqueness
    existing_department = await db.execute(
        select(Department).where(
            Department.code == department_data.code,
            Department.deleted_at.is_(None)
        )
    )
    if existing_department.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department code already exists"
        )

    # Create department
    db_department = Department(
        **department_data.model_dump(),
        created_at=settings.datetime_now
    )
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department


async def update_department(
    db: AsyncSession,
    department_id: int,
    department_data: DepartmentUpdate
) -> Optional[Department]:
    # Check if department exists
    department = await get_department_by_id(db, department_id)
    if not department:
        return None

    update_data = department_data.model_dump(exclude_unset=True)

    # Check unit if being updated
    if "unit_id" in update_data:
        unit = await get_unit_by_id(db, update_data["unit_id"])
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit does not exist"
            )

    # Check parent if being updated
    if "parent_id" in update_data:
        parent_id = update_data["parent_id"]
        if parent_id:
            # Prevent setting itself as parent
            if parent_id == department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department cannot be its own parent"
                )

            parent = await get_department_by_id(db, parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department does not exist"
                )
            if parent.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department is inactive"
                )

            # Check for circular reference in the hierarchy
            current_parent = parent
            while current_parent:
                if current_parent.id == department_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Circular reference detected in department hierarchy"
                    )
                current_parent = await get_department_by_id(
                    db, current_parent.parent_id) if current_parent.parent_id else None

    # Check code uniqueness if being updated
    if "code" in update_data:
        existing_department = await db.execute(
            select(Department).where(
                Department.code == update_data["code"],
                Department.id != department_id,
                Department.deleted_at.is_(None)
            )
        )
        if existing_department.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department code already exists"
            )

    for field, value in update_data.items():
        setattr(department, field, value)

    await db.commit()
    await db.refresh(department)
    return department


async def delete_department(db: AsyncSession, department_id: int) -> bool:
    department = await get_department_by_id(db, department_id)
    if not department:
        return False

    department.deleted_at = settings.datetime_now
    await db.commit()
    return True
