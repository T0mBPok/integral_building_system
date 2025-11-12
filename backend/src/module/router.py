from fastapi import APIRouter, Depends, HTTPException, Path
from src.module.schemas import GetModule, AddModule, UpdateModule
from src.module.rb import RBModule
from src.module.logic import ModuleLogic

router = APIRouter(prefix="/module", tags=["Работа с модулями"])

@router.get("/", response_model=list[GetModule])
async def get_modules(request: RBModule = Depends()):
    return await ModuleLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetModule)
async def get_module_by_id(id: str):
    module = await ModuleLogic.get_one_or_none_by_id(id=id)
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")
    return module

@router.post("/", response_model=GetModule)
async def add_module(data: AddModule):
    return await ModuleLogic.add(**data.model_dump())

@router.put("/{id}", response_model=GetModule)
async def update_module(id: str, data: UpdateModule):
    await ModuleLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await ModuleLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_module(id: str):
    await ModuleLogic.delete(id=id)
    return {"message": f"Модуль с id={id} успешно удалён"}