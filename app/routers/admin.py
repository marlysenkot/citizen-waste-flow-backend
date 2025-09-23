from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os, shutil

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.base_location import Location
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.models.complaint import Complaint, ComplaintStatus
from app.models.waste import CollectionStatus, WasteCollection
from passlib.context import CryptContext

from app.schemas.collector import CollectorResponse
from app.schemas.location import LocationCreate, LocationResponse
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    CategoryCreate,
    CategoryResponse
)
from app.schemas.complaint import ComplaintResponse
from app.schemas.user import UserResponse
from app.schemas.waste import WasteCollectionResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ensure upload directory exists
UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
    return db.query(User).filter(User.role == UserRole.collector).all()


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
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form("active"),
    features: Optional[str] = Form(None),  # comma-separated
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # Handle image upload
    image_filename = None
    if image:
        image_filename = image.filename
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    features_list = features.split(",") if features else []

    new_prod = Product(
        name=name,
        category_id=category_id,
        price=price,
        stock=stock,
        description=description,
        status=status,
        features=features_list,
        image=image_filename
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


@router.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Product).all()


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    features: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(404, "Product not found")

    if name: prod.name = name
    if category_id: prod.category_id = category_id
    if price is not None: prod.price = price
    if stock is not None: prod.stock = stock
    if description: prod.description = description
    if status: prod.status = status
    if features: prod.features = features.split(",")

    if image:
        image_filename = image.filename
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        prod.image = image_filename

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
@router.get("/users", response_model=List[UserResponse])
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


# ----------------- Locations -----------------

@router.post("/locations", response_model=LocationResponse)
def create_location(
    loc: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    new_loc = Location(name=loc.name, address=loc.address)
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@router.get("/locations", response_model=List[LocationResponse])
def list_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return db.query(Location).all()

@router.put("/locations/{loc_id}", response_model=LocationResponse)
def update_location(
    loc_id: int,
    loc: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    location = db.query(Location).get(loc_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    location.name = loc.name
    location.address = loc.address
    db.commit()
    db.refresh(location)
    return location

# --- DELETE Route ---
@router.delete("/locations/{loc_id}", response_model=dict)
def delete_location(
    loc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    location = db.query(Location).get(loc_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(location)
    db.commit()
    return {"detail": "Location deleted successfully"}
