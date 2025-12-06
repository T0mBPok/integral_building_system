from beanie import Link
from fastapi import APIRouter, Depends, HTTPException, Path
from src.indicator.schemas import GetIndicator, AddIndicator, UpdateIndicator
from src.indicator.rb import RBIndicator
from src.indicator.logic import IndicatorLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/indicator", tags=["Работа с индикаторами"])

@router.get("/", response_model=list[GetIndicator])
async def get_indicators(request: RBIndicator = Depends(), user=Depends(get_current_user)):
    print(**request.to_dict())
    return await IndicatorLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetIndicator)
async def get_indicator_by_id(id: str = Path(...), user=Depends(get_current_user)):
    indicator = await IndicatorLogic.get_one_or_none_by_id(id=id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Индикатор не найден")
    return indicator

@router.post("/", response_model=GetIndicator)
async def add_indicator(data: AddIndicator = Depends(AddIndicator.as_form), user=Depends(get_current_user)):
    return await IndicatorLogic.indicator_add(user, **data.to_dict())

@router.put("/{id}", response_model=GetIndicator)
async def update_indicator(data: UpdateIndicator, id: str = Path(...), user=Depends(get_current_user)):
    await IndicatorLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await IndicatorLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_indicator(id: str = Path(...), user=Depends(get_current_user)):
    await IndicatorLogic.delete(id=id)
    return {"message": f"Индикатор с id={id} успешно удалён"}
