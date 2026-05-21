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


class UploadIndicatorsResponse(BaseModel):
    indicators: list[UploadIndicatorResponse]
    created_count: int = 0


class IndicatorFileSheetResponse(BaseModel):
    name: str | None = None
    years: list[str] = Field(default_factory=list)
    region_count: int = 0


class GetIndicatorFile(MongoBaseModel):
    name: str
    description: str | None = None
    original_file_name: str | None = None
    sheets: list[IndicatorFileSheetResponse] = Field(default_factory=list)
    years: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ExtractIndicatorsRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    years: list[str] = Field(default_factory=list)
    sheet_name: str | None = None
    indicator_names: dict[str, str] = Field(default_factory=dict)


class IndicatorFilePreviewSheet(BaseModel):
    name: str | None = None
    years: list[str] = Field(default_factory=list)
    region_count: int = 0


class IndicatorFilePreviewResponse(BaseModel):
    sheets: list[IndicatorFilePreviewSheet] = Field(default_factory=list)
    years: list[str] = Field(default_factory=list)
