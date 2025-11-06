from pydantic import BaseModel, Field
from typing import Optional


class BaseModule(BaseModel):
    level_id: int = Field(..., description="ID уровня, к которому относится модуль", example=1)
    name: str = Field(..., description="Название модуля", example="load_avg")
    value: int = Field(..., description="Значение модуля", example=75)


class GetModule(BaseModule):
    id: int

    class Config:
        from_attributes = True


class AddModule(BaseModule):
    @classmethod
    def as_form(cls, level_id: int, name: str, value: int):
        return cls(level_id=level_id, name=name, value=value)


class UpdateModule(BaseModel):
    level_id: Optional[int] = Field(None, description="ID уровня")
    name: Optional[str] = Field(None, description="Название модуля")
    value: Optional[int] = Field(None, description="Значение модуля")