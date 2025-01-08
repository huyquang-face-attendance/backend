from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.area import Area, AreaCreate, AreaUpdate
import app.services.area as area_service
from app.models import User
from app.schemas.common import PaginationResponse


router = APIRouter()


@router.get("", response_model=PaginationResponse[Area])
async def get_areas(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    unit_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
):
    """
    Retrieve areas.
    """
    areas = await area_service.get_areas(
        db, unit_id=unit_id, page=page, size=size, name=name, code=code, status=status
    )
    return areas


@router.post("", response_model=Area)
async def create_new_area(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    area_in: AreaCreate
):
    """
    Create new area.
    """
    area = await area_service.create_area(db, area_in)
    return area


@router.get("/{area_id}", response_model=Area)
async def read_area(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    area_id: int
):
    """
    Get area by ID.
    """
    area = await area_service.get_area_by_id(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area


@router.put("/{area_id}", response_model=Area)
async def update_existing_area(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    area_id: int,
    area_in: AreaUpdate
):
    """
    Update an area.
    """
    area = await area_service.update_area(db, area_id, area_in)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area


@router.delete("/{area_id}", response_model=bool)
async def delete_existing_area(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    area_id: int
):
    """
    Delete an area.
    """
    success = await area_service.delete_area(db, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return success


@router.get("/by-name/{name}", response_model=Area)
async def read_area_by_name(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    name: str
):
    """
    Get area by name.
    """
    area = await area_service.get_area_by_name(db, name)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area
