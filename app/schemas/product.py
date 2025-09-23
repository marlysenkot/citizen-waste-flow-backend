from pydantic import BaseModel
from typing import Optional, List

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
    status: Optional[str] = "active"  # "active" or "inactive"
    features: Optional[List[str]] = []
    image: Optional[str] = None  # URL or filename

class ProductCreate(ProductBase):
    category_id: int  # link to category

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    features: Optional[List[str]] = None
    category_id: Optional[int] = None
    image: Optional[str] = None  # handle upload separately in endpoint

class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse

    class Config:
        orm_mode = True
