from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class CollectionStatus(str, Enum):
    requested = "requested"
    in_progress = "in_progress"
    completed = "completed"

class WasteCollectionBase(BaseModel):
    location: str

class WasteCollectionCreate(WasteCollectionBase):
    pass

class WasteCollectionResponse(WasteCollectionBase):
    id: int
    status: CollectionStatus
    created_at: datetime
    collector_id: Optional[int]
    class Config:
        from_attributes = True
