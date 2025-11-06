from pydantic import BaseModel, Field

class BaseFunction(BaseModel):
    level_id: int = Field(..., description="ID уровня")
    name: str = Field(..., description="Название функции", example="load_avg")
    expression: str = Field(..., description="Функция")


class GetFunction(BaseFunction):
    id: int

    class Config:
        from_attributes = True 


class AddFunction(BaseFunction):
    @classmethod
    def as_form(cls, level_id: int, name: str, expression: int):
        """Позволяет использовать Depends(AddFunction.as_form)"""
        return cls(level_id=level_id, name=name, expression=expression)


class UpdateFunction(BaseModel):
    level_id: int | None = None
    name: str | None = None
    expression: int | None = None