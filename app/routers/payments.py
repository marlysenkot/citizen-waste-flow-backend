# app/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
from app.core.config import settings
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    MonetbilPaymentCreate,
    MonetbilPaymentResponse,
    MonetbilQuickPaymentRequest
)
from app.db.session import get_db
from app.core.deps import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

# -------------------- Full Monetbil Payment --------------------
@router.post("/monetbil", response_model=MonetbilPaymentResponse)
def make_payment(
    request: MonetbilPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).get(request.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(403, "You cannot pay for this order")

    operator = request.operator or "CM_MTNMOBILEMONEY"

    payload = {
        "amount": str(order.total_price),
        "currency": "XAF",
        "phone": request.phone,
        "operator": operator,
        "country": "CM",
        "item_ref": str(order.id),
        "payment_ref": f"ORD-{order.id}",
        "user": str(current_user.id),
        "first_name": request.first_name or getattr(current_user, "username", ""),
        "last_name": request.last_name or "",
        "email": request.email or getattr(current_user, "email", ""),
        "return_url": "https://yourwebsite.com/return",
        "notify_url": "https://yourapi.com/payments/monetbil/webhook",
        "logo": "https://yourwebsite.com/logo.png"
    }

    full_url = f"{settings.MONETBIL_API_URL}/{settings.MONETBIL_SERVICE_KEY}"

    try:
        resp = requests.post(
            full_url,
            json=payload,
            auth=(settings.MONETBIL_SERVICE_KEY, settings.MONETBIL_SECRET_KEY),
            timeout=30
        )
        print("Monetbil status code:", resp.status_code)
        print("Monetbil response text:", resp.text)
        response = resp.json()
    except Exception as e:
        raise HTTPException(500, f"Payment request failed: {e}")

    if not response.get("success"):
        raise HTTPException(400, f"Monetbil rejected payment: {response.get('message')}")

    payment_ref = response.get("payment_ref") or f"ORD-{order.id}"
    payment_url = response.get("payment_url")

    payment = Payment(
        user_id=current_user.id,
        order_id=order.id,
        amount=order.total_price,
        status=PaymentStatus.pending,
        reference=payment_ref
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return MonetbilPaymentResponse(
        id=payment.id,
        amount=payment.amount,
        order_id=payment.order_id,
        operator=operator,
        status=payment.status,
        payment_ref=payment_ref,
        payment_url=payment_url,
        created_at=payment.created_at
    )


# -------------------- Quick Monetbil Payment --------------------
@router.post("/monetbil/quick", response_model=MonetbilPaymentResponse)
def make_quick_payment(
    request: MonetbilQuickPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).get(request.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(403, "You cannot pay for this order")

    operator = getattr(request, "operator", "CM_MTNMOBILEMONEY")

    payload = {
        "amount": str(order.total_price),
        "currency": "XAF",
        "phone": request.phone,
        "operator": operator,
        "country": "CM",
        "item_ref": str(order.id),
        "payment_ref": f"ORD-{order.id}",
        "user": str(current_user.id),
        "first_name": getattr(current_user, "first_name", current_user.username),
        "last_name": getattr(current_user, "last_name", ""),
        "email": getattr(current_user, "email", ""),
        "return_url": "http://localhost:8000/citizens/products",
        "notify_url": "https://localhost:8000/payments/monetbil/webhook",
        "logo": "https://yourwebsite.com/logo.png"
    }

    full_url = f"{settings.MONETBIL_API_URL}/{settings.MONETBIL_SERVICE_KEY}"

    try:
        resp = requests.post(
            full_url,
            json=payload,
            auth=(settings.MONETBIL_SERVICE_KEY, settings.MONETBIL_SECRET_KEY),
            timeout=30
        )
        print("Monetbil status:", resp.status_code)
        print("Monetbil response:", resp.text)
        response = resp.json()
    except Exception as e:
        raise HTTPException(500, f"Payment request failed: {e}")

    if not response.get("success"):
        raise HTTPException(400, f"Monetbil rejected payment: {response.get('message')}")

    payment_ref = response.get("payment_ref") or f"ORD-{order.id}"
    payment_url = response.get("payment_url")

    payment = Payment(
        user_id=current_user.id,
        order_id=order.id,
        amount=order.total_price,
        status=PaymentStatus.pending,
        reference=payment_ref
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return MonetbilPaymentResponse(
        id=payment.id,
        amount=payment.amount,
        order_id=payment.order_id,
        operator=operator,
        status=payment.status,
        payment_ref=payment_ref,
        payment_url=payment_url,
        created_at=payment.created_at
    )


# -------------------- Monetbil Webhook --------------------
@router.post("/monetbil/webhook")
async def monetbil_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Monetbil calls this webhook to update payment status
    """
    try:
        data = await request.json()  # Monetbil sends JSON
    except Exception:
        return {"message": "Invalid request"}

    payment_ref = data.get("payment_ref")
    status = data.get("status")  # "success" or "failed"

    payment = db.query(Payment).filter(Payment.reference == payment_ref).first()
    if not payment:
        return {"message": "Payment not found"}

    if status == "success":
        payment.status = PaymentStatus.success
        order = db.query(Order).get(payment.order_id)
        if order:
            order.status = OrderStatus.delivered
    elif status == "failed":
        payment.status = PaymentStatus.failed

    db.commit()
    return {"message": "Webhook processed"}
