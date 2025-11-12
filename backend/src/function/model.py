from beanie import Document, Link
from src.level.model import Level

class Function(Document):
    name: str
    expression: str
    level: Link[Level] | None = None

    class Settings:
        name = "functions"