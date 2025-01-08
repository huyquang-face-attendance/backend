from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Unit
from app.schemas.unit import UnitCreate, UnitUpdate, Unit as UnitSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService

settings = get_settings()

# Create unit pagination service
unit_pagination = BasePaginationService[Unit, UnitSchema](
    model=Unit,
    schema=UnitSchema
)


async def get_unit_by_id(db: AsyncSession, unit_id: int) -> Optional[Unit]:
    query = select(Unit).where(Unit.id == unit_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_units(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    parent_id: Optional[int] = None
) -> PaginationResponse[UnitSchema]:
    """Get paginated list of units"""
    return await unit_pagination.get_paginated(
        db,
        page=page,
        size=size,
        parent_id=parent_id
    )


async def get_unit_by_code(db: AsyncSession, code: str) -> Optional[Unit]:
    query = select(Unit).where(Unit.code == code)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_unit(
    db: AsyncSession,
    unit_data: UnitCreate
) -> Unit:
    # Check if code already exists
    existing_unit = await db.execute(
        select(Unit).where(
            Unit.code == unit_data.code,
            Unit.deleted_at.is_(None)
        )
    )
    if existing_unit.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit code already exists"
        )

    # Validate parent_id if provided
    if unit_data.parent_id:
        parent_unit = await get_unit_by_id(db, unit_data.parent_id)
        if not parent_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent unit does not exist"
            )
        if parent_unit.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent unit is inactive"
            )

    db_unit = Unit(
        **unit_data.model_dump(),
        created_at=settings.datetime_now
    )
    db.add(db_unit)
    await db.commit()
    await db.refresh(db_unit)
    return db_unit


async def get_unit_children_with_pagination(
    db: AsyncSession,
    unit_id: int,
    page: int = 1,
    size: int = 10
) -> PaginationResponse[UnitSchema]:
    """Get paginated list of unit's children"""
    return await get_units(db, page=page, size=size, parent_id=unit_id)


async def update_unit(
    db: AsyncSession,
    unit_id: int,
    unit_data: UnitUpdate
) -> Optional[Unit]:
    """Update a unit"""
    unit = await get_unit_by_id(db, unit_id)
    if not unit:
        return None

    if unit.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit is inactive"
        )

    update_data = unit_data.model_dump(exclude_unset=True)

    # Check code uniqueness if being updated
    if "code" in update_data:
        existing_unit = await db.execute(
            select(Unit).where(
                Unit.code == update_data["code"],
                Unit.id != unit_id,
                Unit.deleted_at.is_(None)
            )
        )
        if existing_unit.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit code already exists"
            )

    # Validate parent_id if it's being updated
    if "parent_id" in update_data:
        parent_id = update_data["parent_id"]
        if parent_id:
            parent_unit = await get_unit_by_id(db, parent_id)
            if not parent_unit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent unit does not exist"
                )
            if parent_unit.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent unit is inactive"
                )
            # Prevent circular reference
            if parent_id == unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unit cannot be its own parent"
                )

    for field, value in update_data.items():
        setattr(unit, field, value)

    await db.commit()
    await db.refresh(unit)
    return unit


async def delete_unit(
    db: AsyncSession,
    unit_id: int
) -> bool:
    """Soft delete a unit"""
    unit = await get_unit_by_id(db, unit_id)
    if not unit or unit.deleted_at:
        return False

    unit.deleted_at = settings.datetime_now
    await db.commit()
    return True
