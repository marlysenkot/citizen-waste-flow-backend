from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.waste import WasteCollection
from app.models.complaint import Complaint
from app.schemas.waste import WasteCollectionCreate, WasteCollectionResponse
from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.schemas.user import UserResponse
from app.core.security import get_password_hash

router = APIRouter(prefix="/citizens", tags=["Citizens"])

# Request waste collection
@router.post("/collections", response_model=WasteCollectionResponse)
def request_collection(data: WasteCollectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = WasteCollection(user_id=current_user.id, location=data.location)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

# Submit complaint
@router.post("/complaints", response_model=ComplaintResponse)
def create_complaint(data: ComplaintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    complaint = Complaint(user_id=current_user.id, description=data.description)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

# View complaints
@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Complaint).filter(Complaint.user_id == current_user.id).all()

# View collection history
@router.get("/collections", response_model=List[WasteCollectionResponse])
def list_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WasteCollection).filter(WasteCollection.user_id == current_user.id).all()

# Get profile
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Update profile
@router.put("/profile", response_model=UserResponse)
def update_profile(username: str, password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.username = username or current_user.username
    if password:
        current_user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return current_user