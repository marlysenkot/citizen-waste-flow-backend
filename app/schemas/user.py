from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    citizen = "citizen"
    collector = "collector"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.citizen

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
