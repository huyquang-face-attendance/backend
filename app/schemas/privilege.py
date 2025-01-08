from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PrivilegeBase(BaseModel):
    name: str
    description: Optional[str] = None
    method_route: str


class PrivilegeCreate(PrivilegeBase):
    pass


class PrivilegeUpdate(PrivilegeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    method_route: Optional[str] = None
    deleted_at: Optional[datetime] = None


class Privilege(PrivilegeBase):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
