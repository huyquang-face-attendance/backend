from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_permissions
from app.services import unit as unit_service
from app.schemas.unit import Unit, UnitCreate, UnitUpdate
from app.schemas.common import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[Unit])
async def get_units(
    page: int = 1,
    size: int = 10,
    parent_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewUnit"]))
):
    """Get paginated list of units"""
    return await unit_service.get_units(
        db, page=page, size=size, parent_id=parent_id
    )


@router.post("", response_model=Unit)
async def create_unit(
    unit_data: UnitCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageUnit"]))
):
    return await unit_service.create_unit(db, unit_data)


@router.get("/{unit_id}", response_model=Unit)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewUnit"]))
):
    unit = await unit_service.get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return unit


@router.put("/{unit_id}", response_model=Unit)
async def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageUnit"]))
):
    unit = await unit_service.update_unit(db, unit_id, unit_data)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return unit


@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ManageUnit"]))
):
    if not await unit_service.delete_unit(db, unit_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return {"message": "Unit successfully deleted"}


@router.get("/{unit_id}/children", response_model=PaginationResponse[Unit])
async def get_unit_children(
    unit_id: int,
    page: int = 0,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permissions(["ViewUnit"]))
):
    """Get paginated list of unit's children"""
    unit = await unit_service.get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return await unit_service.get_unit_children_with_pagination(
        db, unit_id, page=page, size=size
    )
