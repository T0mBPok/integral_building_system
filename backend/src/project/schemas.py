from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.base import MongoBaseModel


class IndicatorShort(MongoBaseModel):
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class ProjectIndicatorRefSchema(BaseModel):
    indicator_id: str
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class ProjectCustomIndicatorSchema(BaseModel):
    name: str
    formula: str
    description: str | None = None

    class Config:
        from_attributes = True


class ProjectNormalizationEntrySchema(BaseModel):
    indicator_name: str
    method: str = "minmax"
    output_name: str | None = None

    class Config:
        from_attributes = True


class ProjectWeightEntrySchema(BaseModel):
    indicator_name: str
    weight: float

    class Config:
        from_attributes = True


class ProjectRegionValueSchema(BaseModel):
    region: str
    value: float | None = None

    class Config:
        from_attributes = True


class ProjectCalculatedIndicatorSchema(BaseModel):
    name: str
    regions: list[str] = Field(default_factory=list)
    years: list[str] = Field(default_factory=list)
    values: list[list[float | None]] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ProjectCalculationResultSchema(BaseModel):
    year: str
    normalized_indicators: list[ProjectCalculatedIndicatorSchema] = Field(default_factory=list)
    weight_method: str = "equal"
    weights: list[ProjectWeightEntrySchema] = Field(default_factory=list)
    weighted_components: list[ProjectCalculatedIndicatorSchema] = Field(default_factory=list)
    integral_values: list[ProjectRegionValueSchema] = Field(default_factory=list)
    ranking: list[ProjectRegionValueSchema] = Field(default_factory=list)
    aggregation_method: str = "sum"
    calculated_at: datetime | None = None

    class Config:
        from_attributes = True


class BaseProject(MongoBaseModel):
    name: str
    description: str
    indicators: list[ProjectIndicatorRefSchema] = Field(default_factory=list)
    custom_indicators: list[ProjectCustomIndicatorSchema] = Field(default_factory=list)
    normalization_settings: list[ProjectNormalizationEntrySchema] = Field(default_factory=list)
    weight_settings: list[ProjectWeightEntrySchema] = Field(default_factory=list)
    weight_method: str = "equal"
    calculation_year: str | None = None
    aggregation_method: str = "sum"
    last_result: ProjectCalculationResultSchema | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GetProject(BaseProject):
    class Config:
        from_attributes = True


class AddProject(BaseModel):
    name: str
    description: str
    indicators: list[ProjectIndicatorRefSchema] = Field(default_factory=list)
    custom_indicators: list[ProjectCustomIndicatorSchema] = Field(default_factory=list)
    normalization_settings: list[ProjectNormalizationEntrySchema] = Field(default_factory=list)
    weight_settings: list[ProjectWeightEntrySchema] = Field(default_factory=list)
    weight_method: str = "equal"
    calculation_year: str | None = None
    aggregation_method: str = "sum"


class UpdateProject(BaseModel):
    name: str | None = None
    description: str | None = None
    indicators: list[ProjectIndicatorRefSchema] | None = None
    custom_indicators: list[ProjectCustomIndicatorSchema] | None = None
    normalization_settings: list[ProjectNormalizationEntrySchema] | None = None
    weight_settings: list[ProjectWeightEntrySchema] | None = None
    weight_method: str | None = None
    calculation_year: str | None = None
    aggregation_method: str | None = None


class ProjectCalculateRequest(BaseModel):
    year: str | None = None
    normalization_settings: list[ProjectNormalizationEntrySchema] | None = None
    weight_settings: list[ProjectWeightEntrySchema] | None = None
    weight_method: str | None = None


class ProjectIndicatorAttachRequest(BaseModel):
    indicator_id: str
    name: str | None = None
    description: str | None = None
