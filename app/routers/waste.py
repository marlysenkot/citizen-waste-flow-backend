from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.waste import WasteCollectionCreate, WasteCollectionResponse
from app.models.waste import WasteCollection
from app.db.session import get_db

router = APIRouter(prefix="/waste", tags=["Waste Collection"])

@router.post("/", response_model=WasteCollectionResponse)
def request_collection(req: WasteCollectionCreate, db: Session = Depends(get_db)):
    db_req = WasteCollection(location=req.location, user_id=1)  # TODO: replace with logged-in user
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return db_req

@router.get("/", response_model=List[WasteCollectionResponse])
def list_collections(db: Session = Depends(get_db)):
    return db.query(WasteCollection).all()
