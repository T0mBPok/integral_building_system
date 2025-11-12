from beanie import Document, Link
from typing import Optional, List
from src.user.model import User
from src.level.model import Level

class Project(Document):
    user: Link[User]
    name: str
    description: str
    levels: List[Link["Level"]] | None = None

    class Settings:
        name = "projects"