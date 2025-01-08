from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import PersonType
from app.schemas.person_type import PersonTypeCreate, PersonTypeUpdate, PersonType as PersonTypeSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService

settings = get_settings()

# Create person type pagination service
person_type_pagination = BasePaginationService[PersonType, PersonTypeSchema](
    model=PersonType,
    schema=PersonTypeSchema
)


async def get_person_type_by_id(db: AsyncSession, type_id: int) -> Optional[PersonType]:
    query = select(PersonType).where(
        PersonType.id == type_id,
        PersonType.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_person_type_by_name(db: AsyncSession, name: str) -> Optional[PersonType]:
    """Get person type by name"""
    query = select(PersonType).where(
        PersonType.name == name,
        PersonType.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_person_types(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    name: Optional[str] = None,
    status: Optional[bool] = None
) -> PaginationResponse[PersonTypeSchema]:
    """Get paginated list of person types"""
    filters = {
        "name": name,
        "status": status
    }
    return await person_type_pagination.get_paginated(
        db,
        page=page,
        size=size,
        **filters
    )


async def create_person_type(
    db: AsyncSession,
    person_type_data: PersonTypeCreate
) -> PersonType:
    # Check name uniqueness
    existing_type = await get_person_type_by_name(db, person_type_data.name)
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person type with this name already exists"
        )

    db_person_type = PersonType(
        **person_type_data.model_dump(),
        created_at=settings.datetime_now
    )
    db.add(db_person_type)
    await db.commit()
    await db.refresh(db_person_type)
    return db_person_type


async def update_person_type(
    db: AsyncSession,
    type_id: int,
    person_type_data: PersonTypeUpdate
) -> Optional[PersonType]:
    person_type = await get_person_type_by_id(db, type_id)
    if not person_type:
        return None

    update_data = person_type_data.model_dump(exclude_unset=True)

    # Check name uniqueness if name is being updated
    if "name" in update_data:
        existing_type = await get_person_type_by_name(db, update_data["name"])
        if existing_type and existing_type.id != type_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person type with this name already exists"
            )

    for field, value in update_data.items():
        setattr(person_type, field, value)

    await db.commit()
    await db.refresh(person_type)
    return person_type


async def delete_person_type(db: AsyncSession, type_id: int) -> bool:
    person_type = await get_person_type_by_id(db, type_id)
    if not person_type:
        return False

    person_type.deleted_at = settings.datetime_now
    await db.commit()
    return True
