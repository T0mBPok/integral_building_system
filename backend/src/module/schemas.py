from pydantic import BaseModel, Field

class BaseModule(BaseModel):
    module_id: int = Field(..., description="ID модуля, к которому относится индикатор")
    name: str = Field(..., description="Название индикатора", example="load_avg")
    value: int = Field(..., description="Значение индикатора", example=75)


class GetModule(BaseModule):
    id: int

    class Config:
        from_attributes = True 


class AddModule(BaseModule):
    @classmethod
    def as_form(cls, module_id: int, name: str, value: int):
        return cls(module_id=module_id, name=name, value=value)


class UpdateModule(BaseModel):
    module_id: int | None = None
    name: str | None = None
    value: int | None = None