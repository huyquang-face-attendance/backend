from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.person_event import PersonEvent, PersonEventCreate
import app.services.person_event as person_event_service
from app.models import User
from app.schemas.common import PaginationResponse

router = APIRouter()


@router.get("", response_model=PaginationResponse[PersonEvent])
async def get_person_events(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1),
    person_id: Optional[str] = None,
    device_id: Optional[int] = None,
    area_id: Optional[int] = None,
    person_type_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    gender: Optional[bool] = None,
    identity_card: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    Retrieve person events with various filters.
    """
    return await person_event_service.get_person_events(
        db,
        page=page,
        page_size=page_size,
        person_id=person_id,
        device_id=device_id,
        area_id=area_id,
        person_type_id=person_type_id,
        name=name,
        code=code,
        gender=gender,
        identity_card=identity_card,
        start_time=start_time,
        end_time=end_time
    )


@router.post("", response_model=PersonEvent)
async def create_new_person_event(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    event_in: PersonEventCreate
):
    """
    Create new person event.
    """
    event = await person_event_service.create_person_event(db, event_in)
    return event


@router.get("/{event_id}", response_model=PersonEvent)
async def read_person_event(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    event_id: str
):
    """
    Get person event by ID.
    """
    event = await person_event_service.get_person_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Person event not found")
    return event


@router.get("/latest/{person_id}", response_model=PersonEvent)
async def read_latest_person_event(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    person_id: str,
    device_id: Optional[int] = None
):
    """
    Get latest person event.
    """
    event = await person_event_service.get_latest_person_event(db, person_id, device_id)
    if not event:
        raise HTTPException(
            status_code=404, detail="No events found for this person")
    return event


@router.delete("/{event_id}", response_model=bool)
async def delete_existing_person_event(
    *,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
    event_id: str
):
    """
    Delete a person event.
    """
    success = await person_event_service.delete_person_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person event not found")
    return success
