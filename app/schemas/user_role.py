from pydantic import BaseModel
from datetime import datetime


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int


class UserRoleCreate(UserRoleBase):
    pass


class UserRole(UserRoleBase):
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
