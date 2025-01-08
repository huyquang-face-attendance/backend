from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models import PersonEvent, Person, Camera
from app.schemas.person_event import PersonEventCreate, PersonEvent as PersonEventSchema
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService
import uuid
from app.services.person import get_person_by_id
from app.services.camera import get_camera_by_id
from sqlalchemy.exc import IntegrityError

settings = get_settings()

# Create person event pagination service
person_event_pagination = BasePaginationService[PersonEvent, PersonEventSchema](
    model=PersonEvent,
    schema=PersonEventSchema
)


async def get_person_event_by_id(db: AsyncSession, event_id: str) -> Optional[PersonEvent]:
    query = select(PersonEvent).where(
        PersonEvent.event_id == event_id,
        PersonEvent.deleted_at.is_(None)
    ).options(
        selectinload(PersonEvent.person),
        selectinload(PersonEvent.device)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_person_events(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 100,
    is_unknown: bool = False,
    person_id: Optional[str] = None,
    device_id: Optional[int] = None,
    area_id: Optional[int] = None,
    person_type_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    gender: Optional[bool] = None,
    identity_card: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> PaginationResponse[PersonEventSchema]:
    """Get paginated list of person events with filters"""
    # Initialize base query with joins and relationships
    query = (
        select(PersonEvent)
        .outerjoin(Person, PersonEvent.person_id == Person.id)
        .outerjoin(Camera, PersonEvent.device_id == Camera.id)
        .options(
            selectinload(PersonEvent.person),
            selectinload(PersonEvent.device)
        )
    )

    # Build where conditions
    conditions = []

    # Add deleted_at filter
    conditions.append(PersonEvent.deleted_at.is_(None))

    # Add filters
    if is_unknown:
        conditions.append(PersonEvent.person_id.is_(None))
    elif person_id:
        conditions.append(PersonEvent.person_id == person_id)

    if device_id:
        conditions.append(PersonEvent.device_id == device_id)
    if area_id:
        conditions.append(Camera.area_id == area_id)
    if person_type_id:
        conditions.append(Person.type == person_type_id)
    if name:
        conditions.append(Person.name.ilike(f"%{name}%"))
    if code:
        conditions.append(Person.code == code)
    if gender is not None:
        conditions.append(
            (Person.gender == gender) |
            (Person.id.is_(None) & (PersonEvent.gender == gender))
        )
    if identity_card:
        conditions.append(Person.identity_card == identity_card)
    if start_time:
        conditions.append(PersonEvent.access_time >= start_time)
    if end_time:
        conditions.append(PersonEvent.access_time <= end_time)

    # Apply all conditions
    query = query.where(*conditions)

    # Add ordering
    query = query.order_by(desc(PersonEvent.access_time))

    # Get paginated results
    result = await person_event_pagination.get_paginated(
        db,
        page=page,
        size=page_size,
        query=query
    )

    return result


async def create_person_event(db: AsyncSession, event_data: PersonEventCreate) -> PersonEvent:
    try:
        # Create event directly - let the database handle uniqueness
        event_dict = event_data.model_dump()
        event_dict['created_at'] = settings.datetime_now

        db_event = PersonEvent(**event_dict)
        db.add(db_event)
        await db.flush()  # This will raise an error if event_id exists

        # Only check device and person if the event is new
        device = await get_camera_by_id(db, event_data.device_id)
        if not device:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device does not exist"
            )

        if event_data.person_id:
            person = await get_person_by_id(db, event_data.person_id)
            if not person:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Person does not exist"
                )

        await db.commit()
        return db_event

    except IntegrityError as e:
        await db.rollback()
        if "uq_person_event_event_id" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event ID already exists"
            )
        raise


async def delete_person_event(db: AsyncSession, event_id: str) -> bool:
    event = await get_person_event_by_id(db, event_id)
    if not event:
        return False

    event.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def get_latest_person_event(
    db: AsyncSession,
    person_id: str,
    device_id: Optional[int] = None
) -> Optional[PersonEvent]:
    query = (
        select(PersonEvent)
        .where(
            PersonEvent.person_id == person_id,
            PersonEvent.deleted_at.is_(None)
        )
        .options(
            selectinload(PersonEvent.person),
            selectinload(PersonEvent.device)
        )
    )

    if device_id:
        query = query.where(PersonEvent.device_id == device_id)

    query = query.order_by(desc(PersonEvent.access_time)).limit(1)
    result = await db.execute(query)
    return result.scalar_one_or_none()
