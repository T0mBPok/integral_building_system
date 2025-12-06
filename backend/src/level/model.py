from beanie import Document, Link
from typing import List

from pymongo import IndexModel, ASCENDING
from src.module.model import Module
from src.function.model import Function

class Level(Document):
    project: Link["Project"]
    number: int
    function: Link["Function"] | None = None
    modules: List[Link["Module"]] | None = None

    class Settings:
        name = "levels"
        indexes = [
            IndexModel(
                [("project", ASCENDING), ("number", ASCENDING)],
                unique=True
            )
        ]