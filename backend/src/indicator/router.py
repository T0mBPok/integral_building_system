from fastapi import APIRouter, Depends, Path
from src.indicator.schemas import GetIndicator, AddIndicator, UpdateIndicator
from src.indicator.rb import RBIndicator
from src.indicator.logic import IndicatorLogic

router = APIRouter(prefix="/indicator", tags=["Работа с индикаторами"])

@router.get("/", summary="Получить список индикаторов", response_model=list[GetIndicator])
async def get_indicators(request_body: RBIndicator = Depends()):
    return await IndicatorLogic.get(**request_body.to_dict())

@router.get("/{id}", summary="Получить индикатор по ID", response_model=GetIndicator)
async def get_indicator_by_id(id: int = Path(..., gt=0)):
    return await IndicatorLogic.get_one_or_none_by_id(id=id)

@router.post("/", summary="Добавить индикатор", response_model=GetIndicator)
async def add_indicator(form_data: AddIndicator = Depends(AddIndicator.as_form)):
    return await IndicatorLogic.add(**form_data.model_dump())

@router.delete("/{id}", summary="Удалить индикатор")
async def delete_indicator(id: int = Path(..., gt=0)):
    await IndicatorLogic.delete(id=id)
    return {"message": f"Индикатор с id={id} успешно удалён!"}

@router.put("/{id}", summary="Обновить индикатор", response_model=GetIndicator)
async def update_indicator(indicator: UpdateIndicator, id: int = Path(..., gt=0)):
    new_data = indicator.model_dump(exclude_unset=True)
    await IndicatorLogic.update_indicator(id=id, **new_data)
    return new_data