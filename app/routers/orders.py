from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.order import OrderCreate, OrderResponse
from app.models.order import Order
from app.models.product import Product
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).get(order.product_id)
    total = product.price * order.quantity
    db_order = Order(product_id=order.product_id, user_id=current_user.id, quantity=order.quantity, total_price=total)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).all()
