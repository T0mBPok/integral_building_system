from pydantic import BaseModel, Field

class BaseProject(BaseModel):
    name: str = Field(..., description="Название проекта", example="load_avg")
    description: str = Field(..., description="Значение проекта", example=75)


class GetProject(BaseProject):
    id: int
    user_id: int = Field(..., description="ID модуля, к которому относится проект")

    class Config:
        from_attributes = True 


class AddProject(BaseProject):
    @classmethod
    def as_form(cls, name: str, description: str):
        """Позволяет использовать Depends(AddProject.as_form)"""
        return cls(name=name, description=description)


class UpdateProject(BaseModel):
    name: str | None = None
    description: str | None = None