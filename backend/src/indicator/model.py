from beanie import Document

class Indicator(Document):
    name: str
    value: int

    class Settings:
        name = "indicators"