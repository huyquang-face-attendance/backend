from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FunctionBase(BaseModel):
    name: str

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None

class Function(FunctionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status: bool

    model_config = {
        "from_attributes": True
    }