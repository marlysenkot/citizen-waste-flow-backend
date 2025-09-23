from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.product import ProductResponse, CategoryCreate, CategoryResponse
from app.models.product import Product, Category
from app.db.session import get_db
import shutil
import os
import uuid

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_cat = Category(name=category.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/", response_model=ProductResponse)
def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: str = Form(...),
    stock: int = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("active"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_path = None
    if image:
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/{UPLOAD_DIR}/{filename}"  # served later with StaticFiles

    db_product = Product(
        name=name,
        category_id=category_id,
        price=price,
        stock=stock,
        description=description,
        status=status,
        image=image_path
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
