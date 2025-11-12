from fastapi import APIRouter, Depends, HTTPException, Path
from src.project.schemas import GetProject, AddProject, UpdateProject
from src.project.rb import RBProject
from src.project.logic import ProjectLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/project", tags=["Работа с проектами"])

@router.get("/", response_model=list[GetProject])
async def get_projects(request: RBProject = Depends(), user=Depends(get_current_user)):
    return await ProjectLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetProject)
async def get_project_by_id(id: str = Path(...)):
    project = await ProjectLogic.get_one_or_none_by_id(id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project

@router.post("/", response_model=GetProject)
async def add_project(form: AddProject = Depends(AddProject.as_form), user=Depends(get_current_user)):
    return await ProjectLogic.add(**form.model_dump(), user_id=user.id)

@router.put("/{id}", response_model=GetProject)
async def update_project(data: UpdateProject, id: str = Path(...)):
    await ProjectLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await ProjectLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_project(id: str = Path(...)):
    await ProjectLogic.delete(id=id)
    return {"message": f"Проект с id={id} удалён"}