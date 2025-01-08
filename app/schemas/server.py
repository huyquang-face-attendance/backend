from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServerBase(BaseModel):
    name: str

class ServerCreate(ServerBase):
    pass

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None

class Server(ServerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: bool

    model_config = {
        "from_attributes": True
    } 