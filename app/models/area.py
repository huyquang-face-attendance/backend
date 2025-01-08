from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Area(TimestampModel):
    __tablename__ = "area"

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey(
        'unit.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100))
    code = Column(String(50))

    # Relationships
    unit = relationship("Unit", back_populates="areas")
    cameras = relationship("Camera", back_populates="area")
