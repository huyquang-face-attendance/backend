from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    totalRecords: int
    currentPage: int
    pageSize: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "items": [],
                "totalRecords": 0,
                "currentPage": 1,
                "pageSize": 10
            }
        }
    }
