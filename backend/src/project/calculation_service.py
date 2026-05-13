from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from fastapi import HTTPException, status

from src.indicator.model import Indicator
from src.math_part.program_math.base_indicator import BaseIndicator
from src.math_part.program_math.norm_indicator import NormalizedIndicator
from src.math_part.program_math.weight_indicator import WeightedIndicator
from src.math_part.program_math.exceptions import MathException
from src.math_part.program_math.utils.parse import format_population_data
from src.project.model import (
    Project,
    ProjectCalculatedIndicator,
    ProjectCalculationResult,
    ProjectCustomIndicator,
    ProjectNormalizationEntry,
    ProjectRegionValue,
    ProjectWeightEntry,
)


@dataclass
class PreparedWeights:
    year: str
    method: str
    weights: list[ProjectWeightEntry]
    mapping: dict[str, float]


class ProjectCalculationService:
    @classmethod
    def calculate(
        cls,
        project: Project,
        source_indicators: list[Indicator],
        year: str | None = None,
        normalization_settings: list[ProjectNormalizationEntry] | None = None,
        weight_settings: list[ProjectWeightEntry] | None = None,
        weight_method: str | None = None,
    ) -> ProjectCalculationResult:
        try:
            base_cube = cls._build_base_cube(project, source_indicators)
            cls._sort_cube_axes(base_cube)
            normalized_cube, normalized_specs = cls._normalize_cube(
                project=project,
                base_cube=base_cube,
                normalization_settings=normalization_settings,
            )
            prepared_weights = cls._prepare_weights(
                project=project,
                normalized_indicator_names=normalized_cube.indicators,
                years=normalized_cube.years,
                year=year,
                weight_settings=weight_settings,
                weight_method=weight_method,
                normalized_cube=normalized_cube,
            )
            weighted_indicator = WeightedIndicator(prepared_weights.mapping)
            weighted_indicator_name = "weighted_project_indicator"
            weighted_indicator.apply_weights(
                cube=normalized_cube,
                year=prepared_weights.year,
                name=weighted_indicator_name,
            )

            weighted_matrix = weighted_indicator.get_weighted_table(weighted_indicator_name)
            integral_values = np.sum(weighted_matrix, axis=0)

            return ProjectCalculationResult(
                year=prepared_weights.year,
                normalized_indicators=[
                    cls._cube_indicator_to_model(normalized_cube, spec.output_name or spec.indicator_name)
                    for spec in normalized_specs
                ],
                weight_method=prepared_weights.method,
                weights=prepared_weights.weights,
                weighted_components=cls._weighted_components_to_models(
                    weighted_indicator=weighted_indicator,
                    weighted_indicator_name=weighted_indicator_name,
                ),
                integral_values=cls._region_values(
                    regions=normalized_cube.regions,
                    values=integral_values,
                ),
                ranking=cls._region_values(
                    regions=normalized_cube.regions,
                    values=integral_values,
                    sort_desc=True,
                ),
                aggregation_method="sum",
            )
        except MathException as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    @classmethod
    def _build_base_cube(cls, project: Project, source_indicators: list[Indicator]) -> BaseIndicator:
        if not project.indicators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="В проекте нет выбранных показателей",
            )

        indicators_by_id = {str(indicator.id): indicator for indicator in source_indicators}
        refs = project.indicators

        cube: BaseIndicator | None = None
        for index, ref in enumerate(refs):
            source = indicators_by_id.get(ref.indicator_id)
            if source is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Показатель с id={ref.indicator_id} не найден",
                )
            formatted = cls._indicator_to_formatted_data(source)
            if index == 0:
                cube = BaseIndicator(formatted, ref.name)
            else:
                cube.add_indicator(formatted, ref.name)

        if cube is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось собрать исходный куб показателей",
            )

        for custom_indicator in project.custom_indicators:
            cls._validate_custom_indicator(custom_indicator)
            cube.create_custom_indicator(custom_indicator.formula, custom_indicator.name)

        return cube

    @classmethod
    def _normalize_cube(
        cls,
        project: Project,
        base_cube: BaseIndicator,
        normalization_settings: list[ProjectNormalizationEntry] | None = None,
    ) -> tuple[NormalizedIndicator, list[ProjectNormalizationEntry]]:
        entries = normalization_settings
        if entries is None:
            entries = project.normalization_settings

        if not entries:
            entries = [
                ProjectNormalizationEntry(indicator_name=name, method="minmax", output_name=name)
                for name in base_cube.indicators
            ]

        normalized_cube = NormalizedIndicator(base_cube)
        for entry in entries:
            output_name = entry.output_name or entry.indicator_name
            normalized_cube.create_normalized_indicator(
                indicator_name=entry.indicator_name,
                method=entry.method,
                new_indicator_name=output_name,
            )
        cls._sort_cube_axes(normalized_cube)
        return normalized_cube, entries

    @classmethod
    def _prepare_weights(
        cls,
        project: Project,
        normalized_indicator_names: list[str],
        years: list[str],
        year: str | None = None,
        weight_settings: list[ProjectWeightEntry] | None = None,
        weight_method: str | None = None,
        normalized_cube: NormalizedIndicator | None = None,
    ) -> PreparedWeights:
        target_year = year or project.calculation_year
        if not target_year:
            if not years:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="В данных проекта отсутствуют годы для расчета",
                )
            target_year = cls._sort_labels(years)[0]

        entries = weight_settings
        if entries is None and weight_method is None:
            entries = project.weight_settings

        selected_method = (weight_method or project.weight_method or "equal").lower()

        if entries:
            selected_method = "manual"
            mapping = cls._normalize_weight_mapping({entry.indicator_name: entry.weight for entry in entries})
        elif selected_method in {"equal", "manual"}:
            default_weight = 1 / len(normalized_indicator_names)
            mapping = {name: default_weight for name in normalized_indicator_names}
        else:
            if normalized_cube is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось рассчитать автоматические веса: нет нормализованных данных",
                )
            mapping = WeightedIndicator.calculate_weights(
                cube=normalized_cube,
                year=target_year,
                method=selected_method,
            )

        if target_year not in years:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Год {target_year} отсутствует в нормализованных данных",
            )

        missing = [name for name in normalized_indicator_names if name not in mapping]
        extra = [name for name in mapping if name not in normalized_indicator_names]
        if missing or extra:
            details: list[str] = []
            if missing:
                details.append(f"нет весов для показателей: {', '.join(missing)}")
            if extra:
                details.append(f"веса заданы для неизвестных показателей: {', '.join(extra)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="; ".join(details),
            )

        ordered_entries = [
            ProjectWeightEntry(indicator_name=name, weight=float(mapping[name]))
            for name in normalized_indicator_names
        ]
        ordered_mapping = {entry.indicator_name: entry.weight for entry in ordered_entries}
        return PreparedWeights(
            year=target_year,
            method=selected_method,
            weights=ordered_entries,
            mapping=ordered_mapping,
        )

    @staticmethod
    def _normalize_weight_mapping(mapping: dict[str, float]) -> dict[str, float]:
        weights = np.asarray(list(mapping.values()), dtype=float)
        if np.any(~np.isfinite(weights)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Веса должны быть конечными числами",
            )
        if np.any(weights < 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Веса не могут быть отрицательными",
            )
        total = float(np.sum(weights))
        if total <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сумма весов должна быть больше 0",
            )
        return {
            indicator_name: float(weight / total)
            for indicator_name, weight in zip(mapping.keys(), weights)
        }

    @classmethod
    def _indicator_to_formatted_data(cls, indicator: Indicator):
        frame = cls._indicator_to_dataframe(indicator)
        return format_population_data(frame)

    @classmethod
    def _indicator_to_dataframe(cls, indicator: Indicator) -> pd.DataFrame:
        header = ["region"] + list(indicator.table.years)
        rows = []
        for region, row_values in zip(indicator.table.regions, indicator.table.values):
            rows.append([region] + list(row_values))
        return pd.DataFrame([header] + rows)

    @classmethod
    def _cube_indicator_to_model(
        cls,
        cube: BaseIndicator | NormalizedIndicator,
        indicator_name: str,
    ) -> ProjectCalculatedIndicator:
        indicator_data = cube.get_indicator_data(indicator_name)
        if indicator_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Не удалось получить данные показателя '{indicator_name}'",
            )
        return ProjectCalculatedIndicator(
            name=indicator_name,
            regions=list(cube.regions),
            years=list(cube.years),
            values=cls._matrix_to_list(indicator_data),
        )

    @classmethod
    def _weighted_components_to_models(
        cls,
        weighted_indicator: WeightedIndicator,
        weighted_indicator_name: str,
    ) -> list[ProjectCalculatedIndicator]:
        metadata = weighted_indicator.weighted_indicators[weighted_indicator_name]
        data = metadata["data"]
        indicators = metadata["indicators"]
        regions = metadata["regions"]
        year = metadata["year"]

        components: list[ProjectCalculatedIndicator] = []
        for idx, indicator_name in enumerate(indicators):
            column = data[idx, :]
            values = [[cls._to_float(value)] for value in column]
            components.append(
                ProjectCalculatedIndicator(
                    name=indicator_name,
                    regions=list(regions),
                    years=[year],
                    values=values,
                )
            )
        return components

    @classmethod
    def _region_values(
        cls,
        regions: Iterable[str],
        values: Iterable[float | np.floating],
        sort_desc: bool = False,
    ) -> list[ProjectRegionValue]:
        pairs = [
            ProjectRegionValue(region=region, value=cls._to_float(value))
            for region, value in zip(regions, values)
        ]
        if sort_desc:
            pairs.sort(key=lambda item: float("-inf") if item.value is None else item.value, reverse=True)
        return pairs

    @classmethod
    def _sort_cube_axes(cls, cube: BaseIndicator | NormalizedIndicator) -> None:
        region_order = cls._sort_labels(cube.regions)
        year_order = cls._sort_labels(cube.years)

        region_indices = [cube.region_to_idx[label] for label in region_order]
        year_indices = [cube.year_to_idx[label] for label in year_order]

        cube.cube = cube.cube[np.ix_(region_indices, year_indices, range(cube.cube.shape[2]))]
        cube.regions = region_order
        cube.years = year_order
        cube.region_to_idx = {region: idx for idx, region in enumerate(region_order)}
        cube.year_to_idx = {year: idx for idx, year in enumerate(year_order)}

    @staticmethod
    def _sort_labels(labels: list[str]) -> list[str]:
        def sort_key(value: str):
            try:
                return (0, int(value))
            except (TypeError, ValueError):
                return (1, str(value))

        return sorted(labels, key=sort_key)

    @staticmethod
    def _matrix_to_list(matrix: np.ndarray) -> list[list[float | None]]:
        result: list[list[float | None]] = []
        for row in matrix:
            result.append([ProjectCalculationService._to_float(value) for value in row])
        return result

    @staticmethod
    def _to_float(value) -> float | None:
        if value is None:
            return None
        if isinstance(value, (float, np.floating)) and np.isnan(value):
            return None
        return float(value)

    @staticmethod
    def _validate_custom_indicator(custom_indicator: ProjectCustomIndicator) -> None:
        if '"' not in custom_indicator.formula:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Формула пользовательского показателя '{custom_indicator.name}' должна "
                    "ссылаться на показатели в кавычках, например \"Рождаемость\"/\"Смертность\""
                ),
            )
