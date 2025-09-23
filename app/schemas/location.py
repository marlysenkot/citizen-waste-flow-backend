from pydantic import BaseModel

class LocationBase(BaseModel):
    name: str
    address: str

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    class Config:
        from_attributes = True
