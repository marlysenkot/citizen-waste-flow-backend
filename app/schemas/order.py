from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class OrderStatus(str, Enum):
    pending = "pending"
    delivered = "delivered"
    cancelled = "cancelled"

class OrderBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    total_price: float
    status: OrderStatus
    created_at: datetime
    class Config:
        from_attributes = True
