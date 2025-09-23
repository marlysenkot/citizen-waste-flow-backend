from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import shutil
import os

app = FastAPI()

# --- CATEGORY SCHEMAS ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        orm_mode = True

# --- PRODUCT SCHEMAS ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: Optional[int] = 0
    status: Optional[str] = "active"
    features: List[str] = Field(default_factory=list)  # ✅ never null
    image: Optional[str] = None

class ProductCreate(ProductBase):
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    features: Optional[List[str]] = None
    category_id: Optional[int] = None
    image: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse
    class Config:
        orm_mode = True

# Folder to save uploaded images
UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- ADD PRODUCT ---
@app.post("/admin/products", response_model=ProductResponse)
async def add_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form("active"),
    features: Optional[str] = Form(None),  # comma-separated string
    image: Optional[UploadFile] = File(None)
):
    # Save image if uploaded
    image_filename = None
    if image:
        image_filename = image.filename
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    # Parse features string safely
    features_list = [f.strip() for f in features.split(",")] if features else []

    product = {
        "id": 1,  # In real app, this comes from DB
        "name": name,
        "category": {"id": category_id, "name": "Category Name"},
        "price": price,
        "stock": stock,
        "description": description,
        "status": status,
        "features": features_list,
        "image": image_filename,
    }

    return product

# --- UPDATE PRODUCT ---
@app.put("/admin/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    features: Optional[str] = Form(None),  # comma-separated string
    image: Optional[UploadFile] = File(None)
):
    # Fake existing product (normally from DB)
    product = {
        "id": product_id,
        "name": "Old Name",
        "category": {"id": 1, "name": "Old Category"},
        "price": 100.0,
        "stock": 5,
        "description": "Old desc",
        "status": "active",
        "features": [],
        "image": None
    }

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields
    if name:
        product["name"] = name
    if category_id:
        product["category"] = {"id": category_id, "name": "Updated Category"}
    if price is not None:
        product["price"] = price
    if stock is not None:
        product["stock"] = stock
    if description:
        product["description"] = description
    if status:
        product["status"] = status
    if features is not None:
        product["features"] = [f.strip() for f in features.split(",")] if features else []
    if image:
        image_filename = image.filename
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product["image"] = image_filename

    return product
