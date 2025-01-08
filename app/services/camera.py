from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Camera, Area, Server, Function
from app.schemas.camera import CameraCreate, CameraUpdate, Camera as CameraSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService
from .area import get_area_by_id
from .server import get_server_by_id
from app.models.associations import camera_function

settings = get_settings()

# Create camera pagination service
camera_pagination = BasePaginationService[Camera, CameraSchema](
    model=Camera,
    schema=CameraSchema
)


async def get_camera_by_id(db: AsyncSession, camera_id: int) -> Optional[Camera]:
    query = select(Camera).options(
        selectinload(Camera.functions)
    ).where(
        Camera.id == camera_id,
        Camera.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_cameras(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    unit_id: Optional[int] = None,
    area_id: Optional[int] = None,
    server_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None,
    function_id: Optional[int] = None
) -> PaginationResponse[CameraSchema]:
    """Get paginated list of cameras with additional fields"""
    # Initialize base query with joins and relationships
    query = (
        select(Camera)
        .options(
            selectinload(Camera.area),
            selectinload(Camera.server),
            selectinload(Camera.functions)
        )
    )

    # Build where conditions
    conditions = []

    # Add deleted_at filter
    conditions.append(Camera.deleted_at.is_(None))

    # Filter by unit_id through area
    if unit_id is not None:
        query = query.join(Area)
        conditions.append(Area.unit_id == unit_id)
        conditions.append(Area.deleted_at.is_(None))

    # Add other filters
    filters = {
        "area_id": area_id,
        "server_id": server_id,
        "name": name,
        "code": code,
        "status": status,
    }

    if function_id is not None:
        conditions.append(Camera.functions.any(Function.id == function_id))

    # Apply all conditions
    query = query.where(*conditions)

    # Get paginated results
    result = await camera_pagination.get_paginated(
        db,
        page=page,
        size=size,
        query=query,
        **filters
    )

    # Enhance response items with additional fields and convert functions
    for item in result.items:
        if item.area_id:
            area: Area = await get_area_by_id(db, item.area_id)
            item.area_code = area.code
            item.area_name = area.name
            # Add unit_id from area
            if area:
                item.unit_id = area.unit_id
        if item.server_id:
            server: Server = await get_server_by_id(db, item.server_id)
            item.server_name = server.name

        # Convert functions to the expected format
        item.functions = [
            {"id": f.id, "name": f.name} for f in item.functions
        ]

    return result


async def create_camera(db: AsyncSession, camera_data: CameraCreate) -> Camera:
    # Check if area exists
    area = await get_area_by_id(db, camera_data.area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area does not exist"
        )

    # Check if code already exists
    existing_camera = await db.execute(
        select(Camera).where(
            Camera.code == camera_data.code,
            Camera.deleted_at.is_(None)
        )
    )
    if existing_camera.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera code already exists"
        )

    # Handle server_id
    if camera_data.server_id == 0:  # If server_id is 0, set it to None
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server is required"
        )
    elif camera_data.server_id:  # If server_id is provided and not 0, check if it exists
        server = await get_server_by_id(db, camera_data.server_id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Server does not exist"
            )

    # Create camera data dict excluding functions
    camera_dict = camera_data.model_dump(exclude={'functions'})
    datetime_now = settings.datetime_now
    print("camera datetime_now", datetime_now)
    # Create camera instance
    db_camera = Camera(
        **camera_dict,
        created_at=settings.datetime_now
    )
    db.add(db_camera)
    await db.flush()  # Flush to get camera ID

    # Handle functions if provided
    if camera_data.functions:
        # Check if all functions exist
        existing_functions = await db.execute(
            select(Function)
            .where(
                Function.id.in_(camera_data.functions),
                Function.deleted_at.is_(None)
            )
        )
        existing_functions = existing_functions.scalars().all()
        existing_function_ids = {f.id for f in existing_functions}

        # Verify all requested functions exist
        invalid_functions = set(camera_data.functions) - existing_function_ids
        if invalid_functions:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Functions with IDs {invalid_functions} do not exist"
            )

        # Create camera_function associations
        for function in existing_functions:
            stmt = camera_function.insert().values(
                camera_id=db_camera.id,
                function_id=function.id,
                created_at=settings.datetime_now
            )
            await db.execute(stmt)

    await db.commit()
    await db.refresh(db_camera)

    # Load functions after commit
    await db.refresh(db_camera, ['functions'])
    return db_camera


async def update_camera(
    db: AsyncSession,
    camera_id: int,
    camera_data: CameraUpdate
) -> Optional[Camera]:
    """Update a camera"""
    # Check if camera exists
    camera = await get_camera_by_id(db, camera_id)
    if not camera:
        return None

    # Check if camera is inactive
    if camera.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera is inactive"
        )

    update_data = camera_data.model_dump(exclude_unset=True)
    # Check if area exists
    if "area_id" in update_data:
        area = await get_area_by_id(db, update_data["area_id"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area does not exist"
            )
    # Check code uniqueness if being updated
    if "code" in update_data:
        existing_camera = await db.execute(
            select(Camera).where(
                Camera.code == update_data["code"],
                Camera.id != camera_id,
                Camera.deleted_at.is_(None)
            )
        )
        if existing_camera.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Camera code already exists"
            )

    # Handle functions if provided
    if "functions" in update_data:
        # Check if all functions exist
        existing_functions = await db.execute(
            select(Function)
            .where(
                Function.id.in_(update_data["functions"]),
                Function.deleted_at.is_(None)
            )
        )
        existing_functions = existing_functions.scalars().all()
        existing_function_ids = {f.id for f in existing_functions}

        # Verify all requested functions exist
        invalid_functions = set(
            update_data["functions"]) - existing_function_ids
        if invalid_functions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Functions with IDs {invalid_functions} do not exist"
            )

        # Delete existing camera_function associations
        await db.execute(
            camera_function.delete().where(
                camera_function.c.camera_id == camera_id
            )
        )

        # Create new camera_function associations
        for function in existing_functions:
            stmt = camera_function.insert().values(
                camera_id=camera_id,
                function_id=function.id,
                created_at=settings.datetime_now
            )
            await db.execute(stmt)

        # Remove functions from update_data since we've handled it separately
        del update_data["functions"]

    # Update other fields
    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.commit()
    await db.refresh(camera)
    await db.refresh(camera, ['functions'])
    return camera


async def delete_camera(db: AsyncSession, camera_id: int) -> bool:
    camera = await get_camera_by_id(db, camera_id)
    if not camera:
        return False

    camera.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_cameras_by_area_id(db: AsyncSession, area_id: int) -> List[Camera]:
    query = select(Camera).where(
        Camera.area_id == area_id,
        Camera.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_cameras_by_server_id(db: AsyncSession, server_id: int) -> List[Camera]:
    query = select(Camera).where(
        Camera.server_id == server_id,
        Camera.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_cameras_with_functions(db: AsyncSession) -> List[Camera]:
    query = select(Camera).where(
        Camera.deleted_at.is_(None)
    ).options(
        selectinload(Camera.functions)
    )
    result = await db.execute(query)
    return result.scalars().all()
