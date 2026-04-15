from fastapi import APIRouter, Depends, File, Form, Path, UploadFile

from src.indicator.logic import IndicatorLogic
from src.indicator.schemas import CreateIndicator, GetIndicator, UpdateIndicator, UploadIndicatorResponse
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/indicator", tags=["Работа с показателями"])


@router.get("/", response_model=list[GetIndicator])
async def get_indicators(user=Depends(get_current_user)):
    return await IndicatorLogic.list_for_user(user)


@router.get("/{id}", response_model=GetIndicator)
async def get_indicator_by_id(id: str = Path(...), user=Depends(get_current_user)):
    return await IndicatorLogic.get_for_user(user, id)


@router.post("/", response_model=GetIndicator)
async def create_indicator(data: CreateIndicator, user=Depends(get_current_user)):
    return await IndicatorLogic.create_manual(user, data)


@router.post("/upload", response_model=UploadIndicatorResponse)
async def upload_indicator(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(default=None),
    sheet_name: str | None = Form(default=None),
    user=Depends(get_current_user),
):
    indicator = await IndicatorLogic.upload(
        user=user,
        file=file,
        name=name,
        description=description,
        sheet_name=sheet_name,
    )
    payload = GetIndicator.model_validate(indicator).model_dump()
    payload["preview_region_count"] = len(indicator.table.regions)
    payload["preview_year_count"] = len(indicator.table.years)
    return UploadIndicatorResponse(**payload)


@router.put("/{id}", response_model=GetIndicator)
async def update_indicator(data: UpdateIndicator, id: str = Path(...), user=Depends(get_current_user)):
    return await IndicatorLogic.update_for_user(user, id, data)


@router.delete("/{id}")
async def delete_indicator(id: str = Path(...), user=Depends(get_current_user)):
    await IndicatorLogic.delete_for_user(user, id)
    return {"message": f"Показатель с id={id} успешно удалён"}
