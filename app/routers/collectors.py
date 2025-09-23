from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_collector
from app.models.user import User
from app.models.waste import WasteCollection, CollectionStatus
from app.schemas.waste import WasteCollectionResponse

router = APIRouter(prefix="/collectors", tags=["Collectors"])

# View all collection requests
@router.get("/requests", response_model=List[WasteCollectionResponse])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_collector),
):
    """
    Collectors see all collection requests, regardless of status or assignment.
    """
    return db.query(WasteCollection).all()

# Accept a request
@router.put("/requests/{req_id}/accept", response_model=WasteCollectionResponse)
def accept_request(
    req_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_collector),
):
    req = db.query(WasteCollection).filter(WasteCollection.id == req_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status == CollectionStatus.completed:
        raise HTTPException(400, "Cannot accept a completed request")

    req.collector_id = current_user.id
    req.status = CollectionStatus.in_progress
    db.commit()
    db.refresh(req)
    return req

# Mark as collected
@router.put("/requests/{req_id}/complete", response_model=WasteCollectionResponse)
def complete_request(
    req_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_collector),
):
    req = db.query(WasteCollection).filter(WasteCollection.id == req_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.collector_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    if req.status != CollectionStatus.in_progress:
        raise HTTPException(400, "Request is not in progress")

    req.status = CollectionStatus.completed
    db.commit()
    db.refresh(req)
    return req

# View collector's history
@router.get("/history", response_model=List[WasteCollectionResponse])
def collection_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_collector),
):
    return db.query(WasteCollection).filter(WasteCollection.collector_id == current_user.id).all()
