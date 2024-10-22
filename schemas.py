# schemas.py
from pydantic import BaseModel
from datetime import datetime

class PhotoResponse(BaseModel):
    id: int
    filename: str
    upload_time: datetime

    class Config:
        orm_mode = True

class PhotoMetadata(BaseModel):
    id: int
    filename: str
    upload_time: datetime

    class Config:
        orm_mode = True
