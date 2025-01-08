from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonTypeBase(BaseModel):
    name: str

class PersonTypeCreate(PersonTypeBase):
    pass

class PersonTypeUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None

class PersonType(PersonTypeBase):
    id: int
    status: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    } 