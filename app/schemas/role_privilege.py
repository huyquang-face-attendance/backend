from pydantic import BaseModel
from datetime import datetime

class RolePrivilegeBase(BaseModel):
    role_id: int
    privilege_id: int

class RolePrivilegeCreate(RolePrivilegeBase):
    pass

class RolePrivilege(RolePrivilegeBase):
    created_at: datetime

    model_config = {
        "from_attributes": True
    } 