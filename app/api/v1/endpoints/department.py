from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.department import Department, DepartmentCreate, DepartmentUpdate
import app.services.department as department_service
from app.models import User
from app.schemas.common import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[Department])
async def get_departments(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1),
    unit_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
):
    """
    Retrieve departments.
    """
    departments = await department_service.get_departments(
        db,
        page=page,
        size=size,
        unit_id=unit_id,
        parent_id=parent_id,
        name=name,
        code=code,
        status=status
    )
    return departments


@router.post("", response_model=Department)
async def create_new_department(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    department_in: DepartmentCreate
):
    """
    Create new department.
    """
    department = await department_service.create_department(db, department_in)
    return department


@router.get("/{department_id}", response_model=Department)
async def read_department(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    department_id: int
):
    """
    Get department by ID.
    """
    department = await department_service.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put("/{department_id}", response_model=Department)
async def update_existing_department(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    department_id: int,
    department_in: DepartmentUpdate
):
    """
    Update a department.
    """
    department = await department_service.update_department(db, department_id, department_in)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.delete("/{department_id}", response_model=bool)
async def delete_existing_department(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    department_id: int
):
    """
    Delete a department.
    """
    success = await department_service.delete_department(db, department_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    return success
