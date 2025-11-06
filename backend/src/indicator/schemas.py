from pydantic import BaseModel, Field

class BaseIndicator(BaseModel):
    name: str = Field(..., description="Название индикатора", example="load_avg")
    value: int = Field(..., description="Значение индикатора", example=75)


class GetIndicator(BaseIndicator):
    id: int

    class Config:
        from_attributes = True 


class AddIndicator(BaseIndicator):
    @classmethod
    def as_form(cls, name: str, value: int):
        """Позволяет использовать Depends(AddIndicator.as_form)"""
        return cls(name=name, value=value)


class UpdateIndicator(BaseModel):
    name: str | None = None
    value: int | None = None