from sqlalchemy.orm import class_mapper, selectinload
from typing import TypeVar, Generic, List, Optional, Any, Type, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from app.schemas.common import PaginationResponse
from app.models.base import TimestampModel

ModelType = TypeVar("ModelType", bound=TimestampModel)
SchemaType = TypeVar("SchemaType")


class BasePaginationService(Generic[ModelType, SchemaType]):
    """Base class for pagination services"""

    def __init__(self, model: Type[ModelType], schema: Type[SchemaType]):
        self.model = model
        self.schema = schema

    def _get_relationships(self) -> List[str]:
        """Get all relationship names for the model"""
        mapper = class_mapper(self.model)
        return [rel.key for rel in mapper.relationships]

    def _model_to_dict(self, obj: Any) -> Dict:
        """Convert SQLAlchemy model to dictionary"""
        data = {}
        # Get columns
        for column in class_mapper(obj.__class__).columns.keys():
            data[column] = getattr(obj, column)

        # Handle functions relationship specially for Camera model
        if hasattr(obj, 'functions'):
            data['functions'] = [
                {"id": f.id, "name": f.name}
                for f in obj.functions
                if not f.deleted_at  # Only include non-deleted functions
            ]

        return data

    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        size: int = 10,
        query: Optional[Select] = None,
        **filters: Any
    ) -> PaginationResponse[SchemaType]:
        """
        Get paginated results with optional filters
        """
        # Normalize pagination params
        page = max(1, page)
        size = max(1, min(size, 100))  # Limit max page size
        offset = (page - 1) * size

        # Build base query if not provided
        if query is None:
            query = select(self.model)

        # Add eager loading for all relationships
        for relationship in self._get_relationships():
            query = query.options(selectinload(
                getattr(self.model, relationship)))

        # Add default filter for non-deleted items
        query = query.where(self.model.deleted_at.is_(None))

        # Apply additional filters
        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)

        # Get total count
        count_query = select(func.count()).select_from(
            select(self.model).where(self.model.deleted_at.is_(None))
        )
        total = await db.scalar(count_query)

        # Get paginated data
        query = query.offset(offset).limit(size)
        result = await db.execute(query)
        items = result.unique().scalars().all()

        # Convert to schema
        schema_items = [
            self.schema.model_validate(self._model_to_dict(item)) for item in items
        ]

        # Create response dictionary
        response_data = {
            "totalRecords": total,
            "currentPage": page,
            "pageSize": size,
            "items": schema_items,
        }
        return PaginationResponse[SchemaType](**response_data)
