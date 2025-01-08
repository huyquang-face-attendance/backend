from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Privilege
from app.schemas.privilege import PrivilegeCreate, PrivilegeUpdate, Privilege as PrivilegeSchema
from app.schemas.common import PaginationResponse
from app.core.config import get_settings
from .base import BasePaginationService

settings = get_settings()

# Create privilege pagination service
privilege_pagination = BasePaginationService[Privilege, PrivilegeSchema](
    model=Privilege,
    schema=PrivilegeSchema
)

async def get_privilege_by_id(
    db: AsyncSession,
    privilege_id: int
) -> Optional[Privilege]:
    query = select(Privilege).where(
        Privilege.id == privilege_id,
        Privilege.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_privileges(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10
) -> PaginationResponse[PrivilegeSchema]:
    """Get paginated list of privileges"""
    return await privilege_pagination.get_paginated(
        db,
        page=page,
        size=size
    )


async def create_privilege(
    db: AsyncSession,
    privilege_data: PrivilegeCreate
) -> Privilege:
    db_privilege = Privilege(
        name=privilege_data.name,
        description=privilege_data.description,
        method_route=privilege_data.method_route
    )

    db.add(db_privilege)
    await db.commit()
    await db.refresh(db_privilege)
    return db_privilege


async def update_privilege(
    db: AsyncSession,
    privilege_id: int,
    privilege_data: PrivilegeUpdate
) -> Optional[Privilege]:
    """Update a privilege"""
    privilege = await get_privilege_by_id(db, privilege_id)
    if not privilege:
        return None

    # Update fields
    update_data = privilege_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(privilege, field, value)

    await db.commit()
    await db.refresh(privilege)
    return privilege


async def delete_privilege(
    db: AsyncSession,
    privilege_id: int
) -> bool:
    """Soft delete a privilege"""
    privilege = await get_privilege_by_id(db, privilege_id)
    if not privilege:
        return False

    privilege.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_privilege_by_name(db: AsyncSession, name: str) -> Optional[Privilege]:
    """Get a privilege by its name"""
    query = select(Privilege).where(
        Privilege.name == name,
        Privilege.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
