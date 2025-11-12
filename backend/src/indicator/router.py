from fastapi import APIRouter, Depends, HTTPException, Path
from src.indicator.schemas import GetIndicator, AddIndicator, UpdateIndicator
from src.indicator.rb import RBIndicator
from src.indicator.logic import IndicatorLogic

router = APIRouter(prefix="/indicator", tags=["Работа с индикаторами"])

@router.get("/", response_model=list[GetIndicator])
async def get_indicators(request: RBIndicator = Depends()):
    return await IndicatorLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetIndicator)
async def get_indicator_by_id(id: str):
    indicator = await IndicatorLogic.get_one_or_none_by_id(id=id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Индикатор не найден")
    return indicator

@router.post("/", response_model=GetIndicator)
async def add_indicator(data: AddIndicator):
    return await IndicatorLogic.add(**data.model_dump())

@router.put("/{id}", response_model=GetIndicator)
async def update_indicator(id: str, data: UpdateIndicator):
    await IndicatorLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await IndicatorLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_indicator(id: str):
    await IndicatorLogic.delete(id=id)
    return {"message": f"Индикатор с id={id} успешно удалён"}