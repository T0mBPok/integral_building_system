from __future__ import annotations

from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from src.indicator.logic import IndicatorLogic
from src.project.calculation_service import ProjectCalculationService
from src.project.model import Project, ProjectIndicatorRef
from src.project.schemas import (
    AddProject,
    ProjectCalculateRequest,
    ProjectIndicatorAttachRequest,
    UpdateProject,
)
from src.user.model import User


class ProjectLogic:
    @staticmethod
    async def list_for_user(user: User) -> list[Project]:
        return await Project.find(Project.user.id == user.id).sort("name").to_list()

    @staticmethod
    async def get_for_user(user: User, project_id: str) -> Project:
        try:
            object_id = PydanticObjectId(project_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден") from exc

        project = await Project.find_one(
            Project.id == object_id,
            Project.user.id == user.id,
        )
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        return project

    @classmethod
    async def create_for_user(cls, user: User, payload: AddProject) -> Project:
        cls._validate_aggregation_method(payload.aggregation_method)
        indicator_ids = [item.indicator_id for item in payload.indicators]
        if indicator_ids:
            await IndicatorLogic.get_many_for_user(user, indicator_ids)

        project = Project(
            user=user,
            **payload.model_dump(),
        )
        return await cls._insert_project(project)

    @classmethod
    async def update_for_user(cls, user: User, project_id: str, payload: UpdateProject) -> Project:
        project = await cls.get_for_user(user, project_id)
        updates = payload.model_dump(exclude_unset=True)
        if "aggregation_method" in updates:
            cls._validate_aggregation_method(updates["aggregation_method"])

        if "indicators" in updates:
            indicator_ids = [item["indicator_id"] for item in updates["indicators"]]
            if indicator_ids:
                await IndicatorLogic.get_many_for_user(user, indicator_ids)

        for field, value in updates.items():
            setattr(project, field, value)

        project.updated_at = datetime.now(timezone.utc)
        await project.save()
        return project

    @classmethod
    async def attach_indicator(
        cls,
        user: User,
        project_id: str,
        payload: ProjectIndicatorAttachRequest,
    ) -> Project:
        project = await cls.get_for_user(user, project_id)
        indicator = await IndicatorLogic.get_for_user(user, payload.indicator_id)

        existing_ids = {item.indicator_id for item in project.indicators}
        if payload.indicator_id in existing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Показатель уже добавлен в проект",
            )

        project.indicators.append(
            ProjectIndicatorRef(
                indicator_id=str(indicator.id),
                name=payload.name or indicator.name,
                description=payload.description if payload.description is not None else indicator.description,
            )
        )
        project.updated_at = datetime.now(timezone.utc)
        await project.save()
        return project

    @classmethod
    async def calculate_for_user(
        cls,
        user: User,
        project_id: str,
        payload: ProjectCalculateRequest,
    ) -> Project:
        project = await cls.get_for_user(user, project_id)
        source_indicators = await IndicatorLogic.get_many_for_user(
            user,
            [item.indicator_id for item in project.indicators],
        )
        result = ProjectCalculationService.calculate(
            project=project,
            source_indicators=source_indicators,
            year=payload.year,
            normalization_settings=payload.normalization_settings,
            weight_settings=payload.weight_settings,
        )
        if payload.year is not None:
            project.calculation_year = payload.year
        if payload.normalization_settings is not None:
            project.normalization_settings = payload.normalization_settings
        if payload.weight_settings is not None:
            project.weight_settings = payload.weight_settings
        project.last_result = result
        project.aggregation_method = "sum"
        project.updated_at = datetime.now(timezone.utc)
        await project.save()
        return project

    @staticmethod
    async def delete_for_user(user: User, project_id: str) -> None:
        project = await ProjectLogic.get_for_user(user, project_id)
        await project.delete()

    @staticmethod
    async def _insert_project(project: Project) -> Project:
        try:
            await project.insert()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        return project

    @staticmethod
    def _validate_aggregation_method(aggregation_method: str | None) -> None:
        if aggregation_method is None:
            return
        if aggregation_method != "sum":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сейчас поддерживается только аддитивная свертка aggregation_method='sum'",
            )
