from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models import Role, Privilege
from app.schemas.role import RoleCreate, RoleUpdate, Role as RoleSchema
from app.schemas.common import PaginationResponse
from app.core.config import get_settings
from datetime import datetime
from .base import BasePaginationService

settings = get_settings()

# Create role pagination service
role_pagination = BasePaginationService[Role, RoleSchema](
    model=Role,
    schema=RoleSchema
)


async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
    query = select(Role).where(
        and_(
            Role.id == role_id,
            Role.deleted_at.is_(None)
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_roles(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10
) -> PaginationResponse[RoleSchema]:
    """Get paginated list of roles"""
    return await role_pagination.get_paginated(
        db,
        page=page,
        size=size
    )


async def create_role(
    db: AsyncSession,
    role_data: RoleCreate
) -> Role:
    # Create role
    db_role = Role(
        name=role_data.name,
        description=role_data.description,
    )

    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def update_role(
    db: AsyncSession,
    role_id: int,
    role_data: RoleUpdate
) -> Optional[Role]:
    role = await get_role_by_id(db, role_id)
    if not role:
        return None

    update_data = role_data.model_dump(exclude_unset=True)
    
    # Handle privileges update if present
    if "privileges" in update_data:
        privilege_ids = update_data.pop("privileges")
        query = select(Privilege).where(
            Privilege.id.in_(privilege_ids),
            Privilege.deleted_at.is_(None)
        )
        result = await db.execute(query)
        privileges = result.scalars().all()
        role.privileges = privileges

    for field, value in update_data.items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: int) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role:
        return False

    role.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    query = select(Role).where(
        Role.name == name,
        Role.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_roles_with_privileges(db: AsyncSession) -> List[Role]:
    query = select(Role).where(
        Role.deleted_at.is_(None)
    ).options(
        selectinload(Role.privileges)
    )
    result = await db.execute(query)
    return result.scalars().all()
