from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.camera import Camera, CameraCreate, CameraUpdate
import app.services.camera as camera_service
from app.models import User
from app.services.base import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[Camera])
async def get_cameras(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1),
    unit_id: Optional[int] = None,
    area_id: Optional[int] = None,
    server_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[str] = None,
    function_id: Optional[int] = None
):
    """
    Retrieve cameras.
    """
    cameras = await camera_service.get_cameras(
        db,
        page=page,
        size=size,
        unit_id=unit_id,
        area_id=area_id,
        server_id=server_id,
        name=name,
        code=code,
        status=status,
        function_id=function_id
    )
    return cameras


@router.post("", response_model=Camera)
async def create_new_camera(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    camera_in: CameraCreate
):
    """
    Create new camera.
    """
    camera = await camera_service.create_camera(db, camera_in)
    return camera


@router.get("/{camera_id}", response_model=Camera)
async def read_camera(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    camera_id: int
):
    """
    Get camera by ID.
    """
    camera = await camera_service.get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=Camera)
async def update_existing_camera(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    camera_id: int,
    camera_in: CameraUpdate
):
    """
    Update a camera.
    """
    camera = await camera_service.update_camera(db, camera_id, camera_in)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.delete("/{camera_id}", response_model=bool)
async def delete_existing_camera(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    camera_id: int
):
    """
    Delete a camera.
    """
    success = await camera_service.delete_camera(db, camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    return success
