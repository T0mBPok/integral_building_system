# src/level/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from src.module.schemas import GetModule
from src.function.schemas import GetFunction


class BaseLevel(BaseModel):
    project_id: int = Field(...)
    number: int = Field(...)
    function_id: Optional[int] = None


class AddLevel(BaseLevel):
    pass


class UpdateLevel(BaseModel):
    number: Optional[int] = None
    function_id: Optional[int] = None


class GetLevel(BaseLevel):
    id: int
    modules: List[GetModule] = []
    function: Optional[GetFunction] = None

    class Config:
        from_attributes = True
