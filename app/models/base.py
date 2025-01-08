from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class TimestampModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=False),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=False),
                        onupdate=func.now())
    deleted_at = Column(DateTime(timezone=False))
    status = Column(Boolean, server_default='true')
