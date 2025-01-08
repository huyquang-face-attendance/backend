from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class User(TimestampModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(100))
    unit_id = Column(Integer, ForeignKey('unit.id', ondelete='SET NULL'))

    # Relationships
    unit = relationship("Unit", back_populates="users")
    roles = relationship("Role", secondary="user_role", back_populates="users")
    sessions = relationship("Session", back_populates="user")
