from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.models.complaint import Complaint, ComplaintStatus
from app.models.waste import CollectionStatus, WasteCollection
from passlib.context import CryptContext
from app.schemas.collector import CollectorResponse
from app.schemas.product import ProductCreate, ProductResponse, CategoryCreate, CategoryResponse
from app.schemas.complaint import ComplaintResponse
from app.schemas.user import UserResponse
from app.schemas.waste import WasteCollectionResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ----------------- Collectors -----------------
@router.post("/collectors", response_model=dict)
def create_collector(
    username: str = Query(None),
    email: str = Query(None),
    password: str = Query(None),
    body: dict = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
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

@router.get("/collectors", response_model=List[CollectorResponse])
def list_collectors(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    collectors = db.query(User).filter(User.role == UserRole.collector).all()
    return collectors

@router.delete("/collectors/{collector_id}", response_model=dict)
def delete_collector(collector_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    collector = db.query(User).filter(User.id == collector_id, User.role == UserRole.collector).first()
    if not collector:
        raise HTTPException(404, "Collector not found")
    db.delete(collector)
    db.commit()
    return {"msg": f"Collector {collector.username} deleted"}

# ----------------- Categories -----------------
@router.post("/categories", response_model=CategoryResponse)
def create_category(cat: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_cat = Category(name=cat.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Category).all()

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, cat: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    category = db.query(Category).get(category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    category.name = cat.name
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    category = db.query(Category).get(category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    db.delete(category)
    db.commit()
    return {"msg": f"Category {category.name} deleted"}

# ----------------- Products -----------------
@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_prod = Product(**product.dict())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod

@router.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Product).all()

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(404, "Product not found")
    for field, value in product.dict().items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod

@router.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(404, "Product not found")
    db.delete(prod)
    db.commit()
    return {"msg": f"Product {prod.name} deleted"}

# ----------------- Complaints -----------------
@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Complaint).all()

@router.put("/complaints/{complaint_id}", response_model=ComplaintResponse)
def resolve_complaint(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    complaint = db.query(Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    complaint.status = ComplaintStatus.resolved
    db.commit()
    db.refresh(complaint)
    return complaint

# ----------------- Orders -----------------
@router.get("/orders", response_model=List[WasteCollectionResponse])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(WasteCollection).order_by(WasteCollection.created_at.desc()).limit(10).all()

# ----------------- Stats -----------------
@router.get("/stats", response_model=dict)
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    total_users = db.query(User).count()
    active_collectors = db.query(User).filter(User.role == UserRole.collector).count()
    today_orders = db.query(WasteCollection).filter(WasteCollection.created_at >= date.today()).count()
    pending_complaints = db.query(Complaint).filter(Complaint.status != ComplaintStatus.resolved).count()
    monthly_revenue = 0
    completion_rate = 0

    return {
        "totalUsers": total_users,
        "activeCollectors": active_collectors,
        "todayOrders": today_orders,
        "pendingComplaints": pending_complaints,
        "monthlyRevenue": monthly_revenue,
        "completionRate": completion_rate
    }

# ----------------- Top Collectors -----------------
@router.get("/top-collectors", response_model=List[dict])
def top_collectors(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    collectors = db.query(User).filter(User.role == UserRole.collector).all()
    results = []
    for c in collectors:
        completed = db.query(WasteCollection).filter(
            WasteCollection.collector_id == c.id,
            WasteCollection.status == CollectionStatus.completed
        ).count()
        rating = 5.0
        earnings = completed * 10
        results.append({
            "name": c.username,
            "collections": completed,
            "rating": rating,
            "earnings": f"${earnings}"
        })
    results.sort(key=lambda x: x["collections"], reverse=True)
    return results[:5]

# ----------------- Users -----------------
@router.get("/users", response_model=list[UserResponse])
def list_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    response = []

    for u in users:
        status = "Active" if u.is_active else "Inactive"
        verified = u.is_active
        response.append(UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            status=status,
            verified=verified
        ))
    return response
