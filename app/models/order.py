from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class OrderStatus(enum.Enum):
    pending = "pending"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
