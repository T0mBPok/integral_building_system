from src.schemas.base import MongoBaseModel
from src.module.schemas import GetModule
from src.function.schemas import GetFunction
from pydantic import BaseModel
from src.project.schemas import GetProject

class AddLevel(BaseModel):
    project_id: str
    number: int
    function_id: str | None = None
    @classmethod
    def as_form(cls, project_id: str, number: int, function_id: str | None = None):
        return cls(project_id=project_id, number=number, function_id=function_id)

class UpdateLevel(MongoBaseModel):
    number: int | None = None
    function_id: str | None = None

class GetLevel(MongoBaseModel):
    project: GetProject
    number: int
    modules: list[GetModule] | None = None
    function: GetFunction | None = None

    class Config:
        from_attributes = True
