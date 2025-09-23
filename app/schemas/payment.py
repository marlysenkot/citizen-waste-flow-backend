from pydantic import BaseModel, HttpUrl
from enum import Enum
from datetime import datetime

# Payment status enum
class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

# Base payment info
class MonetbilPaymentBase(BaseModel):
    amount: float
    order_id: int
    operator: str  = "CM_MTNMOBILEMONEY"

# Create payment request
class MonetbilPaymentCreate(MonetbilPaymentBase):
    phone: str
    first_name: str
    last_name: str
    email: str

# Response from Monetbil
class MonetbilPaymentResponse(MonetbilPaymentBase):
    id: int
    status: PaymentStatus
    payment_ref: str         # Monetbil's unique reference
    payment_url: HttpUrl     # URL where the user completes the payment
    created_at: datetime

    class Config:
        from_attributes = True
        
# app/schemas/payment.py

class MonetbilQuickPaymentRequest(BaseModel):
    order_id: int
    phone: str
    operator: str = "CM_MTNMOBILEMONEY"

