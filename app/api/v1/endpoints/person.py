from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.person import Person, PersonCreate, PersonUpdate, FaceSearchRequest, FaceSearchResponse
import app.services.person as person_service
from app.models import User
from app.schemas.common import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[Person])
async def get_persons(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1),
    unit_id: Optional[int] = None,
    department_id: Optional[int] = None,
    type_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
):
    """
    Retrieve persons.
    """
    persons = await person_service.get_persons(
        db,
        page=page,
        size=size,
        unit_id=unit_id,
        department_id=department_id,
        type_id=type_id,
        name=name,
        code=code,
        status=status
    )
    return persons


@router.post("", response_model=Person)
async def create_new_person(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_in: PersonCreate
):
    """
    Create new person.
    """
    person = await person_service.create_person(db, person_in)
    return person


@router.get("/{person_id}", response_model=Person)
async def read_person(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_id: str
):
    """
    Get person by ID.
    """
    person = await person_service.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=Person)
async def update_existing_person(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_id: str,
    person_in: PersonUpdate
):
    """
    Update a person.
    """
    person = await person_service.update_person(db, person_id, person_in)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.delete("/{person_id}", response_model=bool)
async def delete_existing_person(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_id: str
):
    """
    Delete a person.
    """
    success = await person_service.delete_person(db, person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return success


@router.post("/search-face", response_model=FaceSearchResponse)
async def search_face(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    search_request: FaceSearchRequest
):
    """
    Search for persons by face embedding with unit and department filtering
    """
    if not search_request.base64_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Base64 image is required"
        )

    return await person_service.search_face(
        db,
        base64_image=search_request.base64_image,
        unit_id=search_request.unit_id,
        department_id=search_request.department_id,
        threshold=search_request.threshold,
        num_result=search_request.num_result,
        quality=search_request.quality
    )


@router.post("/search-face-camera", response_model=FaceSearchResponse)
async def search_face_camera(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    search_request: FaceSearchRequest
):
    """
    Search for persons by face embedding with unit and department filtering
    """
    if not search_request.base64_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Base64 image is required"
        )

    return await person_service.search_face_camera(
        db,
        base64_image=search_request.base64_image,
        unit_id=search_request.unit_id,
        department_id=search_request.department_id,
        threshold=search_request.threshold,
        num_result=search_request.num_result,
        quality=search_request.quality
    )
