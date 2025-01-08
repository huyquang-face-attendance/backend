from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel

class Server(TimestampModel):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # Relationships
    cameras = relationship("Camera", back_populates="server") 