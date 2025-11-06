from pydantic import BaseModel, Field
from typing import Optional, List

class LevelShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BaseProject(BaseModel):
    name: str = Field(..., description="Название проекта", example="Проект X")
    description: str = Field(..., description="Описание проекта", example="Проект для анализа производительности")


class GetProject(BaseProject):
    id: int
    user_id: int = Field(..., description="ID пользователя, которому принадлежит проект")
    levels: Optional[List[LevelShort]] = None

    class Config:
        from_attributes = True


class AddProject(BaseProject):
    @classmethod
    def as_form(cls, name: str, description: str):
        """Позволяет использовать Depends(AddProject.as_form)"""
        return cls(name=name, description=description)


class UpdateProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None