from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.person_type import PersonType, PersonTypeCreate, PersonTypeUpdate
import app.services.person_type as person_type_service
from app.models import User
from app.schemas.common import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[PersonType])
async def get_person_types(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1),
    name: Optional[str] = None,
    status: Optional[bool] = None
):
    """
    Retrieve person types.
    """
    return await person_type_service.get_person_types(
        db,
        page=page,
        size=size,
        name=name,
        status=status
    )


@router.post("", response_model=PersonType)
async def create_new_person_type(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_type_in: PersonTypeCreate
):
    """
    Create new person type.
    """
    return await person_type_service.create_person_type(db, person_type_in)


@router.get("/{type_id}", response_model=PersonType)
async def read_person_type(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    type_id: int
):
    """
    Get person type by ID.
    """
    person_type = await person_type_service.get_person_type_by_id(db, type_id)
    if not person_type:
        raise HTTPException(status_code=404, detail="Person type not found")
    return person_type


@router.put("/{type_id}", response_model=PersonType)
async def update_existing_person_type(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    type_id: int,
    person_type_in: PersonTypeUpdate
):
    """
    Update a person type.
    """
    person_type = await person_type_service.update_person_type(
        db, type_id, person_type_in)
    if not person_type:
        raise HTTPException(status_code=404, detail="Person type not found")
    return person_type


@router.delete("/{type_id}", response_model=bool)
async def delete_existing_person_type(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    type_id: int
):
    """
    Delete a person type.
    """
    success = await person_type_service.delete_person_type(db, type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person type not found")
    return success
