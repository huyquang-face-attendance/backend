from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel

class Unit(TimestampModel):
    __tablename__ = "unit"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    code = Column(String(50))
    parent_id = Column(Integer, ForeignKey('unit.id', ondelete='SET NULL'))

    # Relationships
    parent = relationship("Unit", remote_side=[id], backref="children")
    users = relationship("User", back_populates="unit")
    departments = relationship("Department", back_populates="unit")
    areas = relationship("Area", back_populates="unit")
