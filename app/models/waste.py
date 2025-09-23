from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class CollectionStatus(enum.Enum):
    requested = "requested"
    in_progress = "in_progress"
    completed = "completed"

class WasteCollection(Base):
    __tablename__ = "waste_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    location = Column(String, nullable=False)
    status = Column(Enum(CollectionStatus), default=CollectionStatus.requested)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="collections")
    collector = relationship("User", foreign_keys=[collector_id])
