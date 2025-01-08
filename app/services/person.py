from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Person
from app.schemas.person import PersonCreate, PersonUpdate, Person as PersonSchema, FaceSearchResult, FaceSearchResponse, FaceDetectResponse
from app.schemas.common import PaginationResponse
from fastapi import HTTPException, status
from app.core.config import get_settings
from .base import BasePaginationService
from .department import get_department_by_id
from .person_type import get_person_type_by_id
import uuid
import numpy as np
from app.services.department import get_departments
from app.services.unit import get_unit_by_id
import time
from app.utils.helpers import save_base64_image
from app.services.ai import detect_face
import os
from app.core.celery.tasks import save_event_image

settings = get_settings()

# Create person pagination service
person_pagination = BasePaginationService[Person, PersonSchema](
    model=Person,
    schema=PersonSchema
)


async def get_person_by_id(db: AsyncSession, person_id: str) -> Optional[Person]:
    query = select(Person).where(
        Person.id == person_id,
        Person.deleted_at.is_(None)
    ).options(
        selectinload(Person.department)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_persons(
    db: AsyncSession,
    *,
    page: int = 1,
    size: int = 10,
    unit_id: Optional[int] = None,
    department_id: Optional[int] = None,
    type_id: Optional[int] = None,
    name: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[bool] = None
) -> PaginationResponse[PersonSchema]:
    """Get paginated list of persons with filters"""
    # Build base query
    query = (
        select(Person)
        .options(
            selectinload(Person.department)
        )
    )

    # Build where conditions
    conditions = []

    # Add deleted_at filter
    conditions.append(Person.deleted_at.is_(None))

    # Add other filters
    if department_id is not None:
        conditions.append(Person.department_id == department_id)

    if type_id is not None:
        conditions.append(Person.type == type_id)

    if name is not None:
        conditions.append(Person.name.ilike(f"%{name}%"))

    if code is not None:
        conditions.append(Person.code == code)

    if status is not None:
        conditions.append(Person.status == status)

    # Handle unit_id filter through department relationship
    if unit_id is not None:
        # Get all departments in the unit
        departments = await get_departments(db, unit_id=unit_id)
        department_ids = [dept.id for dept in departments.items]
        if department_ids:
            conditions.append(Person.department_id.in_(department_ids))
        else:
            # If no departments found in unit, return empty result
            return PaginationResponse[PersonSchema](
                totalRecords=0,
                currentPage=page,
                pageSize=size,
                items=[]
            )

    # Apply all conditions
    if conditions:
        query = query.where(*conditions)

    # Get paginated results
    return await person_pagination.get_paginated(
        db,
        page=page,
        size=size,
        query=query
    )


async def get_person_by_code(db: AsyncSession, code: str) -> Optional[Person]:
    query = select(Person).where(
        Person.code == code,
        Person.deleted_at.is_(None)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_person(db: AsyncSession, person_data: PersonCreate) -> Person:
    # create person id
    person_id = str(uuid.uuid4())
    # Check if department exists
    department = await get_department_by_id(db, person_data.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department does not exist"
        )

    # Check code uniqueness
    existing_person = await get_person_by_code(db, person_data.code)
    if existing_person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person code already exists"
        )
    # check person_type
    person_type = await get_person_type_by_id(db, person_data.type)
    if not person_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person type does not exist"
        )
    # Check image
    base64_image = person_data.base64_image
    if not base64_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is required"
        )
    # save image
    image_name = await save_base64_image(base64_image, settings.get_person_path, filename=person_id + ".jpg")
    if not image_name:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image"
        )
    print(f"Save image success with name: {image_name}")
    # Call face detection API to get embedding
    detect_result = await detect_face(base64_image)

    # Validate detection quality
    if detect_result.data.quality < settings.REGISTER_MIN_QUALITY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Face image quality is too low: {detect_result.data.quality}. Minimum required: {settings.REGISTER_MIN_QUALITY}"
        )

    # Create person with detected feature
    person_dict = person_data.model_dump()
    person_dict['image'] = image_name
    person_dict['feature'] = detect_result.data.feature
    del person_dict['base64_image']
    db_person = Person(
        id=person_id,
        **person_dict,
        created_at=settings.datetime_now
    )

    db.add(db_person)
    await db.commit()
    await db.refresh(db_person)
    return db_person


async def update_person(
    db: AsyncSession,
    person_id: str,
    person_data: PersonUpdate
) -> Optional[Person]:
    # Check if person exists
    person = await get_person_by_id(db, person_id)
    if not person:
        return None

    update_data = person_data.model_dump(exclude_unset=True)

    # Check department if being updated
    if "department_id" in update_data:
        department = await get_department_by_id(db, update_data["department_id"])
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department does not exist"
            )

    # Check code uniqueness if being updated
    if "code" in update_data:
        existing_person = await db.execute(
            select(Person).where(
                Person.code == update_data["code"],
                Person.id != person_id,
                Person.deleted_at.is_(None)
            )
        )
        if existing_person.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person code already exists"
            )

    # Handle base64_image if provided
    if "base64_image" in update_data:
        base64_image = update_data["base64_image"]

        # Call face detection API to get new embedding
        detect_result = await detect_face(base64_image)

        # Validate detection quality
        if detect_result.data.quality < settings.REGISTER_MIN_QUALITY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face image quality is too low: {detect_result.data.quality}. Minimum required: {settings.REGISTER_MIN_QUALITY}"
            )

        # Save new image
        image_name = await save_base64_image(
            base64_image,
            settings.get_person_path,
            filename=f"{person_id}.jpg"
        )
        if not image_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save image"
            )

        # Update person with new image and feature
        update_data["image"] = image_name
        update_data["feature"] = detect_result.data.feature

        # Remove base64_image from update data since we've handled it
        del update_data["base64_image"]

    # Update other fields
    for field, value in update_data.items():
        setattr(person, field, value)

    await db.commit()
    await db.refresh(person)
    return person


async def delete_person(db: AsyncSession, person_id: str) -> bool:
    person = await get_person_by_id(db, person_id)
    if not person:
        return False

    person.deleted_at = settings.datetime_now
    await db.commit()
    return True


async def search_face(
    db: AsyncSession,
    base64_image: str,
    unit_id: int,
    department_id: Optional[int] = None,
    threshold: float = 0.6,
    quality: float = 0.3,
    num_result: int = 1
) -> FaceSearchResponse:
    """Search for persons by face embedding with unit and department filtering"""
    # Validate unit exists
    unit = await get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit does not exist"
        )

    # Call face detection API
    t = time.time()
    detect_result = await detect_face(base64_image)
    request_time = time.time() - t

    # Validate detection quality
    if detect_result.data.quality < quality:
        # Save unknown face image
        current_time = settings.datetime_now.strftime("%H%M%S")
        image_name = await save_base64_image(
            base64_image,
            os.path.join(settings.get_event_path,
                         settings.datetime_now.strftime("%Y%m%d")),
            filename=f"{current_time}_unknown.jpg"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Face image quality is too low: {detect_result.data.quality}"
        )

    # Adjust threshold if mask is detected
    adjusted_threshold = threshold
    if detect_result.data.wearmask:
        adjusted_threshold = max(0.0, threshold - settings.MASK_THRESHOLD_SUB)
    # Convert embedding to numpy array and normalize
    search_embedding = np.array(detect_result.data.feature)
    search_embedding = search_embedding / np.linalg.norm(search_embedding)
    del detect_result.data.feature

    # Build base query
    query = (
        select(Person)
        .join(Person.department)  # Join with department
        .where(
            Person.deleted_at.is_(None),
            Person.feature.isnot(None),
        )
    )

    # Get all departments in the unit
    departments = await get_departments(db, unit_id=unit_id)
    department_ids = [dept.id for dept in departments.items]
    if not department_ids:
        # Save unknown face image
        current_time = settings.datetime_now.strftime("%H%M%S")
        image_name = await save_base64_image(
            base64_image,
            os.path.join(settings.get_event_path,
                         settings.datetime_now.strftime("%Y%m%d")),
            filename=f"{current_time}_unknown.jpg"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No departments found in the unit"
        )

    # Filter by department_id if provided, otherwise use all departments in unit
    if department_id:
        if department_id not in department_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department does not belong to the specified unit"
            )
        query = query.where(Person.department_id == department_id)
    else:
        query = query.where(Person.department_id.in_(department_ids))

    # Execute query
    result = await db.execute(query)
    persons = result.scalars().all()

    if not persons:
        # Save unknown face image
        current_time = settings.datetime_now.strftime("%H%M%S")
        image_name = await save_base64_image(
            base64_image,
            os.path.join(settings.get_event_path,
                         settings.datetime_now.strftime("%Y%m%d")),
            filename=f"{current_time}_unknown.jpg"
        )
        return FaceSearchResponse(
            request_time=request_time,
            results=[],
            data=[detect_result.data],
            nearest_result=None
        )

    # Calculate similarities for all persons
    similarities = []
    for person in persons:
        if not person.feature:
            continue

        # Convert stored feature to numpy array and normalize
        person_embedding = np.array(person.feature)
        person_embedding = person_embedding / np.linalg.norm(person_embedding)

        # Calculate cosine similarity
        similarity = min(round(
            float(np.dot(search_embedding, person_embedding)), 2) * 2, 1.0)

        # Add to similarities list regardless of threshold
        similarities.append((similarity, person))

    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[0], reverse=True)

    # Get nearest result (highest similarity) regardless of threshold
    nearest_person = similarities[0] if similarities else None
    nearest_result = None
    if nearest_person:
        similarity, person = nearest_person
        nearest_result = FaceSearchResult(
            person_id=person.id,
            name=person.name,
            code=person.code,
            department_id=person.department_id,
            type=person.type,
            similarity=similarity,
            image=person.image
        )

    # Filter results by threshold
    threshold_results = [(s, p)
                         for s, p in similarities if s >= adjusted_threshold]
    # Take top N results
    top_results = threshold_results[:num_result]

    # Save event image asynchronously
    current_time = settings.datetime_now.strftime("%H%M%S")
    event_date_path = os.path.join(settings.get_event_path,
                                   settings.datetime_now.strftime("%Y%m%d"))

    if not top_results:
        # Save as unknown asynchronously
        save_event_image.delay(
            base64_image,
            event_date_path,
            f"{current_time}_unknown.jpg"
        )
        return FaceSearchResponse(
            request_time=request_time,
            results=[],
            data=[detect_result.data],
            nearest_result=nearest_result
        )

    # Save with person code if match found
    matched_person = top_results[0][1]
    save_event_image.delay(
        base64_image,
        event_date_path,
        f"{current_time}_{matched_person.code}.jpg"
    )

    # Convert to response format
    search_results = [
        FaceSearchResult(
            person_id=person.id,
            name=person.name,
            code=person.code,
            department_id=person.department_id,
            type=person.type,
            similarity=similarity,
            image=person.image
        )
        for similarity, person in top_results
    ]

    return FaceSearchResponse(
        request_time=request_time,
        results=search_results,
        data=[detect_result.data],
        nearest_result=nearest_result
    )
