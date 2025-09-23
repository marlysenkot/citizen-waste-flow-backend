from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    products = relationship("Product", back_populates="category")



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    status = Column(String, default="active")
    features = Column(JSON, default=[])
    image = Column(String, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

    orders = relationship("Order", back_populates="product")  # <- fixed