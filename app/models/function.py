from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Function(TimestampModel):
    __tablename__ = "function"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # Relationships
    cameras = relationship(
        "Camera", secondary="camera_function", back_populates="functions")
