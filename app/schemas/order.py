from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.schemas.product import ProductResponse

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
    product: Optional[ProductResponse]
    class Config:
        from_attributes = True

class OrderAdminResponse(BaseModel):
    id: int
    service: str
    customer: str
    customerEmail: Optional[str]
    collector: Optional[str]
    collectorPhone: Optional[str]
    address: Optional[str]
    date: Optional[str]
    time: Optional[str]
    status: str
    price: float
    notes: Optional[str]