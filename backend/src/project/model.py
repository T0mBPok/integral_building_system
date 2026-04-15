from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from src.user.model import User


class ProjectIndicatorRef(BaseModel):
    indicator_id: str
    name: str
    description: str | None = None


class ProjectCustomIndicator(BaseModel):
    name: str
    formula: str
    description: str | None = None


class ProjectNormalizationEntry(BaseModel):
    indicator_name: str
    method: str = "minmax"
    output_name: str | None = None


class ProjectWeightEntry(BaseModel):
    indicator_name: str
    weight: float


class ProjectRegionValue(BaseModel):
    region: str
    value: float | None = None


class ProjectCalculatedIndicator(BaseModel):
    name: str
    regions: list[str] = Field(default_factory=list)
    years: list[str] = Field(default_factory=list)
    values: list[list[float | None]] = Field(default_factory=list)


class ProjectCalculationResult(BaseModel):
    year: str
    normalized_indicators: list[ProjectCalculatedIndicator] = Field(default_factory=list)
    weights: list[ProjectWeightEntry] = Field(default_factory=list)
    weighted_components: list[ProjectCalculatedIndicator] = Field(default_factory=list)
    integral_values: list[ProjectRegionValue] = Field(default_factory=list)
    ranking: list[ProjectRegionValue] = Field(default_factory=list)
    aggregation_method: str = "sum"
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Project(Document):
    user: Link[User]
    name: str
    description: str
    indicators: list[ProjectIndicatorRef] = Field(default_factory=list)
    custom_indicators: list[ProjectCustomIndicator] = Field(default_factory=list)
    normalization_settings: list[ProjectNormalizationEntry] = Field(default_factory=list)
    weight_settings: list[ProjectWeightEntry] = Field(default_factory=list)
    calculation_year: str | None = None
    aggregation_method: str = "sum"
    last_result: ProjectCalculationResult | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "projects"
        indexes = [
            IndexModel(
                [("user", ASCENDING), ("name", ASCENDING)],
                unique=True,
            )
        ]
