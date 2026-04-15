from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile, status

from src.indicator.model import Indicator, IndicatorTable
from src.indicator.schemas import CreateIndicator, IndicatorTableSchema, UpdateIndicator
from src.user.model import User


class IndicatorLogic:
    @staticmethod
    async def list_for_user(user: User) -> list[Indicator]:
        return await Indicator.find(Indicator.user.id == user.id).sort("name").to_list()

    @staticmethod
    async def get_for_user(user: User, indicator_id: str) -> Indicator:
        try:
            object_id = PydanticObjectId(indicator_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Показатель не найден") from exc

        indicator = await Indicator.find_one(
            Indicator.id == object_id,
            Indicator.user.id == user.id,
        )
        if indicator is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Показатель не найден")
        return indicator

    @classmethod
    async def create_manual(cls, user: User, payload: CreateIndicator) -> Indicator:
        indicator = Indicator(
            user=user,
            name=payload.name,
            description=payload.description,
            table=IndicatorTable(**payload.table.model_dump()),
        )
        return await cls._insert_indicator(indicator)

    @classmethod
    async def upload(
        cls,
        user: User,
        file: UploadFile,
        name: str,
        description: str | None = None,
        sheet_name: str | None = None,
    ) -> Indicator:
        table = await cls._read_table(file=file, sheet_name=sheet_name)
        payload = Indicator(
            user=user,
            name=name,
            description=description,
            table=IndicatorTable(**table.model_dump()),
            source_file_name=file.filename,
            source_sheet_name=sheet_name,
        )
        return await cls._insert_indicator(payload)

    @staticmethod
    async def update_for_user(user: User, indicator_id: str, payload: UpdateIndicator) -> Indicator:
        indicator = await IndicatorLogic.get_for_user(user, indicator_id)
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            indicator.name = updates["name"]
        if "description" in updates:
            indicator.description = updates["description"]
        indicator.updated_at = datetime.now(timezone.utc)
        await indicator.save()
        return indicator

    @staticmethod
    async def delete_for_user(user: User, indicator_id: str) -> None:
        indicator = await IndicatorLogic.get_for_user(user, indicator_id)
        await indicator.delete()

    @staticmethod
    async def get_many_for_user(user: User, indicator_ids: list[str]) -> list[Indicator]:
        try:
            object_ids = [PydanticObjectId(indicator_id) for indicator_id in indicator_ids]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Один или несколько indicator_id имеют неверный формат",
            ) from exc
        indicators = await Indicator.find(
            {"_id": {"$in": object_ids}},
            Indicator.user.id == user.id,
        ).to_list()
        found_ids = {str(indicator.id) for indicator in indicators}
        missing = [indicator_id for indicator_id in indicator_ids if indicator_id not in found_ids]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Не найдены показатели: {', '.join(missing)}",
            )
        return indicators

    @staticmethod
    async def _insert_indicator(indicator: Indicator) -> Indicator:
        try:
            await indicator.insert()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        return indicator

    @staticmethod
    async def _read_table(file: UploadFile, sheet_name: str | None = None) -> IndicatorTableSchema:
        extension = Path(file.filename or "").suffix.lower()
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл пустой")

        try:
            if extension in {".xls", ".xlsx"}:
                data_frame = pd.read_excel(BytesIO(content), sheet_name=sheet_name or 0, header=None)
            elif extension == ".csv":
                data_frame = pd.read_csv(StringIO(content.decode("utf-8")), header=None)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поддерживаются только файлы .xls, .xlsx и .csv",
                )
        except UnicodeDecodeError:
            data_frame = pd.read_csv(StringIO(content.decode("cp1251")), header=None)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Не удалось прочитать файл: {exc}",
            ) from exc

        return IndicatorLogic._dataframe_to_table(data_frame)

    @staticmethod
    def _dataframe_to_table(data_frame: pd.DataFrame) -> IndicatorTableSchema:
        if data_frame.shape[0] < 2 or data_frame.shape[1] < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Ожидается таблица, где в первой строке идут годы, "
                    "а в первом столбце названия регионов"
                ),
            )

        years = [str(value).strip() for value in data_frame.iloc[0, 1:].tolist()]
        regions = [str(value).strip() for value in data_frame.iloc[1:, 0].tolist()]
        numeric_values = data_frame.iloc[1:, 1:].apply(pd.to_numeric, errors="coerce")
        values: list[list[float | None]] = []
        for row in numeric_values.values.tolist():
            values.append([None if pd.isna(value) else float(value) for value in row])

        if any(not year or year.lower() == "nan" for year in years):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="В первой строке должны быть указаны годы без пустых значений",
            )
        if any(not region or region.lower() == "nan" for region in regions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="В первом столбце должны быть указаны регионы без пустых значений",
            )

        return IndicatorTableSchema(regions=regions, years=years, values=values)
