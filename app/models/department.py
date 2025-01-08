from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Department(TimestampModel):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    code = Column(String(50))
    unit_id = Column(Integer, ForeignKey(
        'unit.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(Integer, ForeignKey(
        'department.id', ondelete='SET NULL'))
    status = Column(Boolean, default=True)

    # Relationships
    unit = relationship("Unit", back_populates="departments")
    parent = relationship("Department", remote_side=[id], backref="children")
    persons = relationship("Person", back_populates="department")
