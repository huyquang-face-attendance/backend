from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CameraBase(BaseModel):
    name: str
    code: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$',
                      min_length=1, max_length=50)
    area_id: int
    link: Optional[str] = None
    server_id: Optional[int] = None
    functions: Optional[List[int]] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = Field(
        None, pattern=r'^[a-zA-Z0-9_-]+$', min_length=1, max_length=50)
    area_id: Optional[int] = None
    link: Optional[str] = None
    server_id: Optional[int] = None
    functions: Optional[List[int]] = None
    status: Optional[bool] = None


class CameraFunction(BaseModel):
    id: int
    name: str


class Camera(CameraBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: Optional[bool] = None

    # Additional fields
    unit_id: Optional[int] = None
    area_code: Optional[str] = None
    area_name: Optional[str] = None
    server_name: Optional[str] = None
    functions: List[CameraFunction] = []

    model_config = {
        "from_attributes": True
    }
