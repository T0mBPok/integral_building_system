from fastapi import APIRouter, Depends, Path
from src.project.schemas import GetProject, AddProject, UpdateProject
from src.project.rb import RBProject
from src.project.logic import ProjectLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/project", tags=["Работа с проектами"])

@router.get("/", summary="Получить список проектов", response_model=list[GetProject])
async def get_projects(request_body: RBProject = Depends(), user: str = Depends(get_current_user)):
    return await ProjectLogic.get(**request_body.to_dict())

@router.get("/{id}", summary="Получить проект по ID", response_model=GetProject)
async def get_project_by_id(id: int = Path(..., gt=0), user: str = Depends(get_current_user)):
    return await ProjectLogic.get_one_or_none_by_id(id=id)

@router.post("/", summary="Добавить проект", response_model=GetProject)
async def add_project(form_data: AddProject = Depends(AddProject.as_form), user: str = Depends(get_current_user)):
    return await ProjectLogic.add(**form_data.model_dump(), user_id=user.id)

@router.delete("/{id}", summary="Удалить проект")
async def delete_project(id: int = Path(..., gt=0), user: str = Depends(get_current_user)):
    await ProjectLogic.delete(id=id)
    return {"message": f"Проект с id={id} успешно удалён!"}

@router.put("/{id}", summary="Обновить проект", response_model=GetProject)
async def update_project(project: UpdateProject, id: int = Path(..., gt=0), user: str = Depends(get_current_user)):
    new_data = project.model_dump(exclude_unset=True)
    await ProjectLogic.update_project(id=id, **new_data)
    return new_data