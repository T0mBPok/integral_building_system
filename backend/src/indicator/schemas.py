from src.schemas.base import MongoBaseModel
from pydantic import BaseModel

class BaseIndicator(MongoBaseModel):
    name: str
    value: int

class GetIndicator(BaseIndicator):
    id: str

    class Config:
        from_attributes = True

class AddIndicator(BaseModel):
    name: str
    value: int

class UpdateIndicator(MongoBaseModel):
    name: str | None = None
    value: int | None = None