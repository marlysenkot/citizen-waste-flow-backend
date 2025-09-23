from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class ComplaintStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="complaints")
