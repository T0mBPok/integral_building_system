from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile, status

from src.indicator.model import Indicator, IndicatorFile, IndicatorFileSheet, IndicatorTable
from src.indicator.schemas import CreateIndicator, ExtractIndicatorsRequest, IndicatorTableSchema, UpdateIndicator
from src.user.model import User


class IndicatorLogic:
    @staticmethod
    async def list_for_user(user: User) -> list[Indicator]:
        return await Indicator.find(Indicator.user.id == user.id).sort("name").to_list()

    @staticmethod
    async def list_files_for_user(user: User) -> list[IndicatorFile]:
        return await IndicatorFile.find(IndicatorFile.user.id == user.id).sort("-created_at").to_list()

    @staticmethod
    async def get_file_for_user(user: User, file_id: str) -> IndicatorFile:
        try:
            object_id = PydanticObjectId(file_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден") from exc

        indicator_file = await IndicatorFile.find_one(
            IndicatorFile.id == object_id,
            IndicatorFile.user.id == user.id,
        )
        if indicator_file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")
        return indicator_file

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

    @classmethod
    async def upload_many(
        cls,
        user: User,
        file: UploadFile,
        name: str,
        description: str | None = None,
        split_by_year: bool = False,
        years: list[str] | None = None,
    ) -> list[Indicator]:
        tables = await cls._read_tables(file=file)
        indicators: list[Indicator] = []
        multiple_tables = len(tables) > 1
        for table_name, table in tables:
            if split_by_year:
                year_tables = cls._split_table_by_year(table, years)
            else:
                year_tables = [(None, table)]

            for year, year_table in year_tables:
                indicator_name = cls._build_uploaded_indicator_name(
                    base_name=name,
                    sheet_name=table_name if multiple_tables else None,
                    year=year,
                )
                payload = Indicator(
                    user=user,
                    name=indicator_name,
                    description=description,
                    table=IndicatorTable(**year_table.model_dump()),
                    source_file_name=file.filename,
                    source_sheet_name=table_name,
                )
                indicators.append(await cls._insert_indicator(payload))
        return indicators

    @classmethod
    async def upload_file(
        cls,
        user: User,
        file: UploadFile,
        name: str,
        description: str | None = None,
    ) -> IndicatorFile:
        tables = await cls._read_tables(file=file)
        indicator_file = IndicatorFile(
            user=user,
            name=name,
            description=description,
            original_file_name=file.filename,
            sheets=[
                IndicatorFileSheet(
                    name=sheet_name,
                    table=IndicatorTable(**table.model_dump()),
                )
                for sheet_name, table in tables
            ],
        )
        try:
            await indicator_file.insert()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        return indicator_file

    @classmethod
    async def extract_from_file(
        cls,
        user: User,
        file_id: str,
        payload: ExtractIndicatorsRequest,
    ) -> list[Indicator]:
        indicator_file = await cls.get_file_for_user(user, file_id)
        years = [str(year).strip() for year in payload.years if str(year).strip()]
        if not years:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Выберите хотя бы один год",
            )

        selected_sheets = [
            sheet for sheet in indicator_file.sheets
            if payload.sheet_name is None or sheet.name == payload.sheet_name
        ]
        if not selected_sheets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Лист файла не найден",
            )

        indicators: list[Indicator] = []
        multiple_tables = len(indicator_file.sheets) > 1 and payload.sheet_name is None
        indicator_index = 1
        for sheet in selected_sheets:
            table = IndicatorTableSchema.model_validate(sheet.table)
            for year, year_table in cls._split_table_by_year(table, years):
                custom_name = payload.indicator_names.get(year, "").strip()
                indicator_name = custom_name or f"Показатель {indicator_index}"
                indicator = Indicator(
                    user=user,
                    name=indicator_name,
                    description=payload.description or indicator_file.description,
                    table=IndicatorTable(**year_table.model_dump()),
                    source_file_name=indicator_file.original_file_name or indicator_file.name,
                    source_sheet_name=sheet.name,
                )
                indicators.append(await cls._insert_indicator(indicator, ensure_unique_name=True))
                indicator_index += 1
        return indicators

    @staticmethod
    async def delete_file_for_user(user: User, file_id: str) -> None:
        indicator_file = await IndicatorLogic.get_file_for_user(user, file_id)
        await indicator_file.delete()

    @classmethod
    async def preview_file(cls, file: UploadFile):
        tables = await cls._read_tables(file=file)
        return [
            {
                "name": table_name,
                "years": table.years,
                "region_count": len(table.regions),
            }
            for table_name, table in tables
        ]

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
    async def _insert_indicator(indicator: Indicator, ensure_unique_name: bool = False) -> Indicator:
        if ensure_unique_name:
            indicator.name = await IndicatorLogic._unique_indicator_name(indicator.user, indicator.name)
        try:
            await indicator.insert()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        return indicator

    @staticmethod
    async def _unique_indicator_name(user: User, base_name: str) -> str:
        candidate = base_name.strip() or "Показатель"
        existing = await Indicator.find_one(
            Indicator.user.id == user.id,
            Indicator.name == candidate,
        )
        if existing is None:
            return candidate

        suffix = 2
        while True:
            candidate_with_suffix = f"{candidate} ({suffix})"
            existing = await Indicator.find_one(
                Indicator.user.id == user.id,
                Indicator.name == candidate_with_suffix,
            )
            if existing is None:
                return candidate_with_suffix
            suffix += 1

    @staticmethod
    async def _read_table(file: UploadFile, sheet_name: str | None = None) -> IndicatorTableSchema:
        tables = await IndicatorLogic._read_tables(file=file, sheet_name=sheet_name)
        return tables[0][1]

    @staticmethod
    async def _read_tables(
        file: UploadFile,
        sheet_name: str | None = None,
    ) -> list[tuple[str | None, IndicatorTableSchema]]:
        extension = Path(file.filename or "").suffix.lower()
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл пустой")

        try:
            if extension in {".xls", ".xlsx"}:
                if sheet_name:
                    data_frame = pd.read_excel(BytesIO(content), sheet_name=sheet_name, header=None)
                    return [(sheet_name, IndicatorLogic._dataframe_to_table(data_frame))]
                sheets = pd.read_excel(BytesIO(content), sheet_name=None, header=None)
                return [
                    (str(sheet), IndicatorLogic._dataframe_to_table(data_frame))
                    for sheet, data_frame in sheets.items()
                ]
            elif extension == ".csv":
                data_frame = pd.read_csv(StringIO(content.decode("utf-8")), header=None)
                return [(None, IndicatorLogic._dataframe_to_table(data_frame))]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Поддерживаются только файлы .xls, .xlsx и .csv",
                )
        except UnicodeDecodeError:
            data_frame = pd.read_csv(StringIO(content.decode("cp1251")), header=None)
            return [(None, IndicatorLogic._dataframe_to_table(data_frame))]
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Не удалось прочитать файл: {exc}",
            ) from exc

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

    @staticmethod
    def _split_table_by_year(
        table: IndicatorTableSchema,
        selected_years: list[str] | None = None,
    ) -> list[tuple[str, IndicatorTableSchema]]:
        years_to_export = selected_years or table.years
        missing_years = [year for year in years_to_export if year not in table.years]
        if missing_years:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"В файле нет годов: {', '.join(missing_years)}",
            )

        result: list[tuple[str, IndicatorTableSchema]] = []
        for year in years_to_export:
            year_index = table.years.index(year)
            result.append(
                (
                    year,
                    IndicatorTableSchema(
                        regions=table.regions,
                        years=[year],
                        values=[[row[year_index]] for row in table.values],
                    ),
                )
            )
        return result

    @staticmethod
    def _build_uploaded_indicator_name(
        base_name: str,
        sheet_name: str | None = None,
        year: str | None = None,
    ) -> str:
        parts = [base_name]
        if sheet_name:
            parts.append(sheet_name)
        if year:
            parts.append(year)
        return ": ".join(parts)
