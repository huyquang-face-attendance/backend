from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(...,
                          pattern=r'^[a-zA-Z0-9_]+$', min_length=3, max_length=100)
    full_name: Optional[str] = None
    unit_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None, pattern=r'^[a-zA-Z0-9_]+$', min_length=3, max_length=100)
    password: Optional[str] = None
    full_name: Optional[str] = None
    unit_id: Optional[int] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
