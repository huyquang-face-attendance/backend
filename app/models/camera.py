from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Camera(TimestampModel):
    __tablename__ = "camera"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey(
        'area.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100))
    code = Column(String(50))
    link = Column(String(100))
    server_id = Column(Integer, ForeignKey('server.id', ondelete='SET NULL'))
    status = Column(Boolean, default=True)

    # Relationships
    area = relationship("Area", back_populates="cameras")
    server = relationship("Server", back_populates="cameras")
    functions = relationship(
        "Function",
        secondary="camera_function",
        back_populates="cameras"
    )
    person_events = relationship("PersonEvent", back_populates="device")
