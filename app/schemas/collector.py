from pydantic import BaseModel

class CollectorResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
