from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product import ProductCreate, ProductResponse, CategoryCreate, CategoryResponse
from app.models.product import Product, Category
from app.db.session import get_db

router = APIRouter(prefix="/products", tags=["Products"])

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
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
