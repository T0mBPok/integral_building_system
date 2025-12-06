from src.schemas.base import MongoBaseModel
from pydantic import BaseModel

class BaseFunction(MongoBaseModel):
    name: str
    expression: str

class GetFunction(BaseFunction):
    class Config:
        from_attributes = True

class AddFunction(BaseModel):
    name: str
    expression: str
    @classmethod
    def as_form(cls, name: str, expression: str):
        return cls(name=name, expression=expression)

class UpdateFunction(MongoBaseModel):
    name: str | None = None
    expression: str | None = None