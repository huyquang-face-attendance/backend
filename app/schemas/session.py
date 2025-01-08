from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionBase(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime
    refresh_expires_at: datetime


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
