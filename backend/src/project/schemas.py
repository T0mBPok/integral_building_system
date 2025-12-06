from pydantic import Field, BaseModel
from typing import List
from src.schemas.base import MongoBaseModel

class LevelShort(MongoBaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class BaseProject(MongoBaseModel):
    name: str = Field(..., description="Название проекта")
    description: str = Field(..., description="Описание проекта")

class GetProject(BaseProject):
    levels: list[LevelShort] | None = None

    class Config:
        from_attributes = True

class AddProject(BaseModel):
    name: str | None = None
    description: str | None = None
    @classmethod
    def as_form(cls, name: str, description: str):
        return cls(name=name, description=description)

class UpdateProject(MongoBaseModel):
    name: str | None = None
    description: str | None = None