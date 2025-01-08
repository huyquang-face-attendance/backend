from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Role(TimestampModel):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Relationships
    users = relationship("User", secondary="user_role", back_populates="roles")
    privileges = relationship(
        "Privilege", secondary="role_privilege", back_populates="roles")
