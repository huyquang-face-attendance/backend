from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UnitBase(BaseModel):
    name: str
    code: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$',
                      min_length=1, max_length=50)
    parent_id: Optional[int] = None


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = Field(
        None, pattern=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    parent_id: Optional[int] = None
    status: Optional[bool] = None


class Unit(UnitBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: bool

    model_config = {
        "from_attributes": True
    }
