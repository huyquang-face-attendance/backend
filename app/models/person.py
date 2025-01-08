from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel
import uuid


class Person(TimestampModel):
    __tablename__ = "person"

    id = Column(String(36), primary_key=True,
                default=lambda: str(uuid.uuid4()))
    department_id = Column(Integer, ForeignKey(
        'department.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    image = Column(String(100), nullable=False)
    feature = Column(ARRAY(Float, dimensions=1), nullable=False)  # vector(512)
    type = Column(Integer, ForeignKey('person_type.id'), nullable=False)
    # Updated to proper FK
    gender = Column(Boolean)
    birthday = Column(DateTime)
    identity_card = Column(String(20))
    phone = Column(String(20))
    email = Column(String(50))
    status = Column(Boolean, default=True)

    # Relationships
    department = relationship("Department", back_populates="persons")
    events = relationship("PersonEvent", back_populates="person")
    type_info = relationship(
        "PersonType", back_populates="persons")  # Added relationship
