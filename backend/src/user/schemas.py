from pydantic import BaseModel, EmailStr, Field


class SUserRegister(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str
    class Config:
        from_attributes = True 

class SUserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50, description='Пароль от 5 до 50 символов')
    username: str = Field(..., min_length=3, max_length=20, description="Имя от 3 до 20 символов")
    
class SUserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)
    
class SUser(BaseModel):
    id: int
    email: EmailStr
    username: str