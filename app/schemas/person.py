from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class PersonBase(BaseModel):
    # not null
    name: str
    code: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$',
                      min_length=1, max_length=50)
    department_id: int
    type: Optional[int]
    image: Optional[str] = None
    # can be null
    gender: Optional[bool] = None
    birthday: Optional[datetime] = None
    identity_card: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    email: Optional[EmailStr] = None


class PersonCreate(PersonBase):
    base64_image: str


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = Field(
        None, pattern=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    department_id: Optional[int] = None
    type: Optional[int] = None
    gender: Optional[bool] = None
    birthday: Optional[datetime] = None
    identity_card: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    email: Optional[EmailStr] = None
    base64_image: Optional[str] = None
    status: Optional[bool] = None


class Person(PersonBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "exclude": ["feature"]
        }
    }


class FaceSearchRequest(BaseModel):
    base64_image: str
    unit_id: int
    department_id: Optional[int] = None
    threshold: Optional[float] = 0.6
    quality: Optional[float] = 0.3
    num_result: Optional[int] = 1


class FaceDetectResult(BaseModel):
    feature: Optional[list[float]] = None
    face_rectangle: Optional[list[int]] = None
    quality: Optional[float] = None
    wearmask: Optional[bool] = None
    decode_time: Optional[float] = 0
    process_time: Optional[float] = 0


class FaceDetectResponse(BaseModel):
    status_code: int
    message: str
    data: FaceDetectResult


class FaceSearchResult(BaseModel):
    person_id: str
    name: str
    code: str
    department_id: int
    type: Optional[int]
    similarity: float
    image: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class FaceSearchResponse(BaseModel):
    request_time: float = 0
    data: list[FaceDetectResult] = []
    results: list[FaceSearchResult] = []
    nearest_result: Optional[FaceSearchResult] = None

    model_config = {
        "from_attributes": True
    }
