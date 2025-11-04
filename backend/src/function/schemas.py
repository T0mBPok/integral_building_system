from pydantic import BaseModel, Field

class BaseFunction(BaseModel):
    module_id: int = Field(..., description="ID модуля, к которому относится индикатор")
    name: str = Field(..., description="Название индикатора", example="load_avg")
    expression: str = Field(..., description="Функция")


class GetFunction(BaseFunction):
    id: int

    class Config:
        from_attributes = True 


class AddFunction(BaseFunction):
    @classmethod
    def as_form(cls, module_id: int, name: str, expression: int):
        """Позволяет использовать Depends(AddFunction.as_form)"""
        return cls(module_id=module_id, name=name, value=expression)


class UpdateFunction(BaseModel):
    module_id: int | None = None
    name: str | None = None
    expression: int | None = None