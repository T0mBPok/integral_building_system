from beanie import Document, Indexed
from pydantic import EmailStr

class User(Document):
    username: str
    password: str
    email: EmailStr = Indexed(unique=True) 

    class Settings:
        name = "users"