from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PersonEventBase(BaseModel):
    event_id: Optional[str]
    person_id: Optional[str]
    access_time: datetime
    device_id: int
    image: str
    video: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[bool] = None
    score: Optional[float] = None
    quality: Optional[float] = None


class PersonEventCreate(PersonEventBase):
    feature: Optional[list[float]] = None


class PersonEvent(PersonEventBase):
    event_id: str
    feature: Optional[list[float]] = None
    created_at: datetime
    status: bool

    model_config = {
        "from_attributes": True
    }
