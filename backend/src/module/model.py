from beanie import Document, Link
from src.level.model import Level

class Module(Document):
    name: str
    value: int
    level: Link[Level]

    class Settings:
        name = "modules"