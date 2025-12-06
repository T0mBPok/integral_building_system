from beanie import Document, Indexed, Link

class Function(Document):
    name: str = Indexed(unique=True) 
    expression: str = Indexed(unique=True)

    class Settings:
        name = "functions"
