from pydantic import EmailStr, Field, BaseModel
from src.schemas.base import MongoBaseModel

class SUserRegister(MongoBaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=5, max_length=50)
    
class SUserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)
    
class SUser(MongoBaseModel):
    id: str
    email: EmailStr
    username: str

    class Config:
        from_attributes = True
