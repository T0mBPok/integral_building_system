from beanie import Document, Indexed, Link
from typing import List

from pymongo import ASCENDING, IndexModel
from src.user.model import User
from src.level.model import Level

class Project(Document):
    user: Link["User"]
    name: str
    description: str
    levels: List[Link["Level"]] | None = None

    class Settings:
        name = "projects"
        indexes = [
            IndexModel(
                [("user", ASCENDING), ("name", ASCENDING)],
                unique=True
            )
        ]