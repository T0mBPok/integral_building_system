from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from src.user.model import User


class IndicatorTable(BaseModel):
    regions: list[str] = Field(default_factory=list)
    years: list[str] = Field(default_factory=list)
    values: list[list[float | None]] = Field(default_factory=list)


class Indicator(Document):
    user: Link[User]
    name: str
    description: str | None = None
    table: IndicatorTable
    source_file_name: str | None = None
    source_sheet_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "indicators"
        indexes = [
            IndexModel(
                [("user", ASCENDING), ("name", ASCENDING)],
                unique=True,
            )
        ]
