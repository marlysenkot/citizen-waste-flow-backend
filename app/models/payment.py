from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Enum, String
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class PaymentStatus(enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    reference = Column(String, unique=True, index=True) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    order = relationship("Order")

from pydantic import BaseModel

class PaymentRequest(BaseModel):
    order_id: int
    phone: str
