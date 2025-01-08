from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.schemas.common import PaginationResponse
from app.core.security import get_password_hash
from app.core.config import get_settings
from .base import BasePaginationService
from fastapi import HTTPException, status
from app.services.unit import get_unit_by_id
from app.models.role import Role
from sqlalchemy.orm import joinedload
settings = get_settings()

# Create user pagination service
user_pagination = BasePaginationService[User, UserSchema](
    model=User,
    schema=UserSchema
)


async def get_users(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    unit_id: Optional[int] = None
) -> PaginationResponse[UserSchema]:
    """Get paginated list of users"""
    return await user_pagination.get_paginated(
        db,
        page=page,
        size=size,
        unit_id=unit_id
    )


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    query = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.username == username)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_users_with_roles(db: AsyncSession) -> List[User]:
    query = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.deleted_at.is_(None))
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    # Check if user exists
    if await get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already registered"
        )

    # Validate unit_id if provided
    if user_data.unit_id:
        unit = await get_unit_by_id(db, user_data.unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid unit_id: Unit does not exist"
            )
        if unit.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid unit_id: Unit is inactive"
            )

    # Create user instance
    db_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        unit_id=user_data.unit_id,
        created_at=settings.datetime_now
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdate
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is inactive"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    # Validate unit_id if it's being updated
    if "unit_id" in update_data:
        unit_id = update_data["unit_id"]
        if unit_id:
            unit = await get_unit_by_id(db, unit_id)
            if not unit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid unit_id: Unit does not exist"
                )
            if unit.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid unit_id: Unit is inactive"
                )

    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(
            update_data.pop("password"))

    if "roles" in update_data:
        query = select(Role).where(
            Role.id.in_(update_data.pop("roles")),
            Role.deleted_at.is_(None)
        )
        result = await db.execute(query)
        roles = result.scalars().all()
        user.roles = roles

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def get_user_privileges(db: AsyncSession, user_id: int) -> List[str]:
    query = (
        select(User)
        .options(
            joinedload(User.roles).joinedload(Role.privileges)
        )
        .where(User.id == user_id)
    )
    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()

    if not user:
        return []

    # Extract privileges from roles
    privileges = set()
    for role in user.roles:
        for privilege in role.privileges:
            privileges.add(privilege.name)

    return list(privileges)


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    if user.deleted_at:
        return False
    user.deleted_at = settings.datetime_now
    await db.commit()
    return True
