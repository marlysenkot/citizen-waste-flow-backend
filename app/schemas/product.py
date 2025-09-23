from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase): 
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ProductCreate(ProductBase):
    category_id: int

class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse
    class Config:
        from_attributes = True
