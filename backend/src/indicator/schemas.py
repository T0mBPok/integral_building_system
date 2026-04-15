from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from src.schemas.base import MongoBaseModel


class IndicatorTableSchema(BaseModel):
    regions: list[str]
    years: list[str]
    values: list[list[float | None]]

    @model_validator(mode="after")
    def validate_shape(self):
        if len(self.values) != len(self.regions):
            raise ValueError("Количество строк values должно совпадать с количеством regions")
        for row in self.values:
            if len(row) != len(self.years):
                raise ValueError("Каждая строка values должна совпадать по длине с количеством years")
        return self

    class Config:
        from_attributes = True


class BaseIndicator(MongoBaseModel):
    name: str
    description: str | None = None
    table: IndicatorTableSchema
    source_file_name: str | None = None
    source_sheet_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GetIndicator(BaseIndicator):
    class Config:
        from_attributes = True


class CreateIndicator(BaseModel):
    name: str
    description: str | None = None
    table: IndicatorTableSchema


class UpdateIndicator(BaseModel):
    name: str | None = None
    description: str | None = None


class UploadIndicatorResponse(GetIndicator):
    preview_region_count: int = 0
    preview_year_count: int = 0
