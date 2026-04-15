from fastapi import APIRouter, Depends, Path

from src.project.logic import ProjectLogic
from src.project.schemas import (
    AddProject,
    GetProject,
    ProjectCalculateRequest,
    ProjectIndicatorAttachRequest,
    UpdateProject,
)
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/project", tags=["Работа с проектами"])


@router.get("/", response_model=list[GetProject])
async def get_projects(user=Depends(get_current_user)):
    return await ProjectLogic.list_for_user(user)


@router.get("/{id}", response_model=GetProject)
async def get_project_by_id(id: str = Path(...), user=Depends(get_current_user)):
    return await ProjectLogic.get_for_user(user, id)


@router.post("/", response_model=GetProject)
async def add_project(data: AddProject, user=Depends(get_current_user)):
    return await ProjectLogic.create_for_user(user, data)


@router.put("/{id}", response_model=GetProject)
async def update_project(data: UpdateProject, id: str = Path(...), user=Depends(get_current_user)):
    return await ProjectLogic.update_for_user(user, id, data)


@router.post("/{id}/indicators", response_model=GetProject)
async def attach_indicator(
    data: ProjectIndicatorAttachRequest,
    id: str = Path(...),
    user=Depends(get_current_user),
):
    return await ProjectLogic.attach_indicator(user, id, data)


@router.post("/{id}/calculate", response_model=GetProject)
async def calculate_project(
    data: ProjectCalculateRequest,
    id: str = Path(...),
    user=Depends(get_current_user),
):
    return await ProjectLogic.calculate_for_user(user, id, data)


@router.delete("/{id}")
async def delete_project(id: str = Path(...), user=Depends(get_current_user)):
    await ProjectLogic.delete_for_user(user, id)
    return {"message": f"Проект с id={id} удалён"}
