from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.waste import CollectionStatus, WasteCollection
from app.models.complaint import Complaint
from app.schemas.waste import WasteCollectionCreate, WasteCollectionResponse
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.schemas.user import UserResponse
from app.core.security import get_password_hash
from app.schemas.order import OrderCreate, OrderResponse
from app.models.order import Order
from app.models.product import Product

router = APIRouter(prefix="/citizens", tags=["Citizens"])

# ---------------- Waste Collections ----------------
@router.post("/collections", response_model=WasteCollectionResponse)
def request_collection(
    data: WasteCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Citizen requests a new waste collection"""
    req = WasteCollection(
        user_id=current_user.id,
        location=data.location,
        status=CollectionStatus.requested,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/collections", response_model=List[WasteCollectionResponse])
def list_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Citizen views their own collection requests"""
    return (
        db.query(WasteCollection)
        .filter(WasteCollection.user_id == current_user.id)
        .all()
    )

# ---------------- Orders ----------------
@router.post("/orders", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).get(order.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    total = product.price * order.quantity
    db_order = Order(
        product_id=order.product_id,
        user_id=current_user.id,
        quantity=order.quantity,
        total_price=total,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders", response_model=List[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()

# ---------------- Complaints ----------------
@router.post("/complaints", response_model=ComplaintResponse)
def create_complaint(
    data: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = Complaint(user_id=current_user.id, description=data.description)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Complaint).filter(Complaint.user_id == current_user.id).all()

# ---------------- Profile ----------------
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    username: str,
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.username = username or current_user.username
    if password:
        current_user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return current_user
