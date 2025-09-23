from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class UserRole(enum.Enum):
    citizen = "citizen"
    collector = "collector"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.citizen)
    is_active = Column(Boolean, default=True) 
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    complaints = relationship("Complaint", back_populates="user")
    
    # Collections requested by the user
    collections = relationship(
        "WasteCollection",
        back_populates="user",
        foreign_keys="[WasteCollection.user_id]"
    )
    
    # Collections assigned to the user as collector
    assigned_collections = relationship(
        "WasteCollection",
        foreign_keys="[WasteCollection.collector_id]",
        back_populates=None  # no back_populates needed here
    )
