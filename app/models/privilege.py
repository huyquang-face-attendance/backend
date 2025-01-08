from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel

class Privilege(TimestampModel):
    __tablename__ = "privilege"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    method_route = Column(String(100), nullable=False)

    # Relationships
    roles = relationship("Role", secondary="role_privilege", back_populates="privileges")
