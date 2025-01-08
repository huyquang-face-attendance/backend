from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str
    code: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$',
                      min_length=1, max_length=50)
    unit_id: int
    parent_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = Field(
        None, pattern=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    unit_id: Optional[int] = None
    parent_id: Optional[int] = None
    status: Optional[bool] = None


class Department(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: bool

    model_config = {
        "from_attributes": True
    }
