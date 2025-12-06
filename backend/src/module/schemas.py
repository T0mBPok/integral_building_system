from pydantic import BaseModel
from src.schemas.base import MongoBaseModel

class BaseModule(MongoBaseModel):
    level_id: str
    name: str
    value: int

class GetModule(BaseModule):
    class Config:
        from_attributes = True

class AddModule(BaseModel):
    level_id: str
    name: str
    value: int
    @classmethod
    def as_form(cls, level_id: str, name: str, value: int):
        return cls(level_id=level_id, name=name, value=value)

class UpdateModule(MongoBaseModel):
    level_id: str | None = None
    name: str | None = None
    value: int | None = None