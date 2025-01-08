from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class PersonType(TimestampModel):
    __tablename__ = "person_type"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(Boolean, default=True)
    # Relationships
    persons = relationship("Person", back_populates="type_info")
