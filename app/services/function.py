from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Function
from app.schemas.function import FunctionCreate, FunctionUpdate
from app.core.config import get_settings

settings = get_settings()

async def get_function_by_id(db: AsyncSession, function_id: int) -> Optional[Function]:
    query = select(Function).where(
        Function.id == function_id,
        Function.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_functions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Function]:
    query = select(Function).where(
        Function.deleted_at.is_(None)
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_function(db: AsyncSession, function_data: FunctionCreate) -> Function:
    db_function = Function(**function_data.model_dump())
    db.add(db_function)
    await db.commit()
    await db.refresh(db_function)
    return db_function

async def update_function(
    db: AsyncSession,
    function_id: int,
    function_data: FunctionUpdate
) -> Optional[Function]:
    function = await get_function_by_id(db, function_id)
    if not function:
        return None

    update_data = function_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(function, field, value)

    await db.commit()
    await db.refresh(function)
    return function

async def delete_function(db: AsyncSession, function_id: int) -> bool:
    function = await get_function_by_id(db, function_id)
    if not function:
        return False

    function.deleted_at = settings.datetime_now
    await db.commit()
    return True

async def get_function_by_name(db: AsyncSession, name: str) -> Optional[Function]:
    query = select(Function).where(
        Function.name == name,
        Function.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_functions_with_cameras(db: AsyncSession) -> List[Function]:
    query = select(Function).where(
        Function.deleted_at.is_(None)
    ).options(
        selectinload(Function.cameras)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_functions_by_camera_id(db: AsyncSession, camera_id: int) -> List[Function]:
    query = select(Function).join(
        Function.cameras
    ).where(
        Function.deleted_at.is_(None),
        Function.cameras.any(id=camera_id)
    )
    result = await db.execute(query)
    return result.scalars().all() 