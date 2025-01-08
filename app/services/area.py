from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Area
from app.schemas.area import AreaCreate, AreaUpdate, Area as AreaSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService
from .unit import get_unit_by_id
settings = get_settings()

# Create area pagination service
area_pagination = BasePaginationService[Area, AreaSchema](
    model=Area,
    schema=AreaSchema
)


async def get_area_by_id(db: AsyncSession, area_id: int) -> Optional[Area]:
    query = select(Area).where(Area.id == area_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_areas(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    unit_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
) -> PaginationResponse[AreaSchema]:
    """Get paginated list of areas"""
    filters = {
        k: v for k, v in {
            "unit_id": unit_id,
            "name": name,
            "code": code,
            "status": status
        }.items() if v is not None
    }

    return await area_pagination.get_paginated(
        db,
        page=page,
        size=size,
        **filters
    )


async def get_area_by_name(db: AsyncSession, name: str) -> Optional[Area]:
    query = select(Area).where(Area.name == name, Area.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_area(
    db: AsyncSession,
    area_data: AreaCreate
) -> Area:
    # Check if unit exists
    unit = await get_unit_by_id(db, area_data.unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit does not exist"
        )
    # Check if code already exists
    existing_area = await db.execute(
        select(Area).where(
            Area.code == area_data.code,
            Area.deleted_at.is_(None)
        )
    )
    if existing_area.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area code already exists"
        )
    db_area = Area(
        **area_data.model_dump(),
        created_at=settings.datetime_now
    )
    db.add(db_area)
    await db.commit()
    await db.refresh(db_area)
    return db_area


async def update_area(
    db: AsyncSession,
    area_id: int,
    area_data: AreaUpdate
) -> Optional[Area]:
    """Update an area"""
    # Check if area exists
    area = await get_area_by_id(db, area_id)
    if not area:
        return None

    # Check if area is inactive
    if area.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area is inactive"
        )
    update_data = area_data.model_dump(exclude_unset=True)
    # Check if unit exists
    if "unit_id" in update_data:
        unit = await get_unit_by_id(db, update_data["unit_id"])
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit does not exist"
            )
    # Check code uniqueness if being updated
    if "code" in update_data:
        existing_area = await db.execute(
            select(Area).where(
                Area.code == update_data["code"],
                Area.id != area_id,
                Area.deleted_at.is_(None)
            )
        )
        if existing_area.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area code already exists"
            )

    for field, value in update_data.items():
        setattr(area, field, value)

    await db.commit()
    await db.refresh(area)
    return area


async def delete_area(db: AsyncSession, area_id: int) -> bool:
    area = await get_area_by_id(db, area_id)
    if not area:
        return False

    area.deleted_at = settings.datetime_now
    await db.commit()
    return True
