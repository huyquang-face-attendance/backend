from pydantic import BaseModel
from typing import List, Any


class PaginationResponse(BaseModel):
    currentPage: int
    pageSize: int
    totalRecords: int
    data: List[Any]
