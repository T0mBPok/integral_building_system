from beanie import Document, Indexed, Link
from src.user.model import User

class Indicator(Document):
    name: str = Indexed(unique=True) 
    value: int
    user: Link["User"]

    class Settings:
        name = "indicators"