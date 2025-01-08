from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, ARRAY, Float, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class PersonEvent(TimestampModel):
    __tablename__ = "person_event"

    event_id = Column(String(36), primary_key=True)
    person_id = Column(String(36), ForeignKey(
        'person.id', ondelete='CASCADE'), nullable=True)
    access_time = Column(DateTime, nullable=False)
    device_id = Column(Integer, ForeignKey(
        'camera.id', ondelete='SET NULL'), nullable=False)
    image = Column(Text, nullable=False)
    video = Column(Text)
    feature = Column(ARRAY(Float, dimensions=1))  # vector(512)
    age = Column(Integer)
    gender = Column(Boolean)
    score = Column(Float)
    quality = Column(Float)

    # Relationships
    person = relationship("Person", back_populates="events")
    device = relationship("Camera", back_populates="person_events")

    # Indexes
    __table_args__ = (
        Index('ix_person_event_person_id', 'person_id'),
        Index('ix_person_event_device_id', 'device_id'),
        Index('ix_person_event_access_time', 'access_time'),
        Index('ix_person_event_deleted_at', 'deleted_at'),
        Index('ix_person_event_person_time', 'person_id', 'access_time'),
        Index('ix_person_event_device_time', 'device_id', 'access_time'),
    )
