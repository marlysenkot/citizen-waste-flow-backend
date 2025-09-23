from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.product import ProductCreate, ProductResponse, CategoryCreate, CategoryResponse
from app.schemas.complaint import ComplaintResponse
from passlib.context import CryptContext

router = APIRouter(prefix="/admin", tags=["Admin"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/collectors", response_model=dict)
def create_collector(
    username: str = Query(None),
    email: str = Query(None),
    password: str = Query(None),
    body: dict = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # Use JSON body if provided
    if body:
        username = body.get("username", username)
        email = body.get("email", email)
        password = body.get("password", password)

    if not all([username, email, password]):
        raise HTTPException(400, "username, email, and password are required")

    hashed_password = hash_password(password)

    collector = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=UserRole.collector
    )
    db.add(collector)
    db.commit()
    db.refresh(collector)
    return {"msg": f"Collector {collector.username} created"}

@router.get("/collectors", response_model=List[dict])
def list_collectors(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(User).filter(User.role == UserRole.collector).all()

# Manage categories
@router.post("/categories", response_model=CategoryResponse)
def create_category(cat: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_cat = Category(name=cat.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

# Manage products
@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_prod = Product(**product.dict())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod

# View complaints
@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Complaint).all()

# Update complaint status
@router.put("/complaints/{complaint_id}", response_model=ComplaintResponse)
def resolve_complaint(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    complaint = db.query(Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    complaint.status = ComplaintStatus.resolved
    db.commit()
    db.refresh(complaint)
    return complaint
