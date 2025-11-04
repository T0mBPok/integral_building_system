from fastapi import APIRouter, Depends, Path
from src.indicator.schemas import GetModule, AddModule, UpdateModule
from src.indicator.rb import RBModule
from src.indicator.logic import ModuleLogic

router = APIRouter(prefix="/module", tags=["Работа с модулями"])

@router.get("/", summary="Получить список модулей", response_model=list[GetModule])
async def get_indicators(request_body: RBModule = Depends()):
    return await ModuleLogic.get(**request_body.to_dict())

@router.get("/{id}", summary="Получить модуль по ID", response_model=GetModule)
async def get_indicator_by_id(id: int = Path(..., gt=0)):
    return await ModuleLogic.get_one_or_none_by_id(id=id)

@router.post("/", summary="Добавить модуль", response_model=GetModule)
async def add_indicator(form_data: AddModule = Depends(AddModule.as_form)):
    return await ModuleLogic.add(**form_data.model_dump())

@router.delete("/{id}", summary="Удалить модуль")
async def delete_indicator(id: int = Path(..., gt=0)):
    await ModuleLogic.delete(id=id)
    return {"message": f"Индикатор с id={id} успешно удалён!"}

@router.put("/{id}", summary="Обновить модуль", response_model=GetModule)
async def update_indicator(indicator: UpdateModule, id: int = Path(..., gt=0)):
    new_data = indicator.model_dump(exclude_unset=True)
    await ModuleLogic.update_indicator(id=id, **new_data)
    return new_data