from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .privilege import Privilege


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None
    privileges: List[Privilege]

    class Config:
        from_attributes = True


class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    deleted_at: Optional[datetime] = None
    privileges: Optional[List[int]] = None
