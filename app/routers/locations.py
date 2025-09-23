from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.models.base_location import Location
from app.schemas.location import LocationCreate, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.post("/", response_model=LocationResponse)
def create_location(loc: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    new_loc = Location(name=loc.name, address=loc.address)
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@router.get("/", response_model=List[LocationResponse])
def list_locations(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(Location).all()

@router.put("/{loc_id}", response_model=LocationResponse)
def update_location(loc_id: int, loc: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    location = db.query(Location).get(loc_id)
    if not location:
        raise HTTPException(404, "Location not found")
    location.name = loc.name
    location.address = loc.address
    db.commit()
    db.refresh(location)
    return location
