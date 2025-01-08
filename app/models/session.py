from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Session(TimestampModel):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    refresh_expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
