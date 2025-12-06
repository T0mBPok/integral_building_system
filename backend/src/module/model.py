from beanie import Document, Link

class Module(Document):
    name: str
    value: int
    level: "Link[Level]"

    class Settings:
        name = "modules"