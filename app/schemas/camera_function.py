from pydantic import BaseModel
from datetime import datetime

class CameraFunctionBase(BaseModel):
    camera_id: int
    function_id: int

class CameraFunctionCreate(CameraFunctionBase):
    pass

class CameraFunction(CameraFunctionBase):
    created_at: datetime

    model_config = {
        "from_attributes": True
    } 