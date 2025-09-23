from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class ComplaintStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class ComplaintBase(BaseModel):
    description: str

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintResponse(ComplaintBase):
    id: int
    status: ComplaintStatus
    created_at: datetime
    class Config:
        from_attributes = True
