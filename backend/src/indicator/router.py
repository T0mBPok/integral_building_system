from fastapi import APIRouter, Depends, File, Form, Path, UploadFile

from src.indicator.logic import IndicatorLogic
from src.indicator.schemas import (
    CreateIndicator,
    ExtractIndicatorsRequest,
    GetIndicatorFile,
    GetIndicator,
    IndicatorFileSheetResponse,
    IndicatorFilePreviewResponse,
    IndicatorFilePreviewSheet,
    UpdateIndicator,
    UploadIndicatorResponse,
    UploadIndicatorsResponse,
)
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/indicator", tags=["Работа с показателями"])


@router.get("/", response_model=list[GetIndicator])
async def get_indicators(user=Depends(get_current_user)):
    return await IndicatorLogic.list_for_user(user)


def _file_payload(indicator_file) -> GetIndicatorFile:
    years: list[str] = []
    sheets = []
    for sheet in indicator_file.sheets:
        sheet_years = list(sheet.table.years)
        for year in sheet_years:
            if year not in years:
                years.append(year)
        sheets.append(
            IndicatorFileSheetResponse(
                name=sheet.name,
                years=sheet_years,
                region_count=len(sheet.table.regions),
            )
        )
    return GetIndicatorFile(
        id=str(indicator_file.id),
        name=indicator_file.name,
        description=indicator_file.description,
        original_file_name=indicator_file.original_file_name,
        sheets=sheets,
        years=years,
        created_at=indicator_file.created_at,
        updated_at=indicator_file.updated_at,
    )


@router.get("/files/", response_model=list[GetIndicatorFile])
async def get_indicator_files(user=Depends(get_current_user)):
    files = await IndicatorLogic.list_files_for_user(user)
    return [_file_payload(indicator_file) for indicator_file in files]


@router.post("/files/", response_model=GetIndicatorFile)
async def upload_indicator_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(default=None),
    user=Depends(get_current_user),
):
    indicator_file = await IndicatorLogic.upload_file(
        user=user,
        file=file,
        name=name,
        description=description,
    )
    return _file_payload(indicator_file)


@router.post("/files/{id}/extract", response_model=UploadIndicatorsResponse)
async def extract_indicators_from_file(
    data: ExtractIndicatorsRequest,
    id: str = Path(...),
    user=Depends(get_current_user),
):
    indicators = await IndicatorLogic.extract_from_file(user=user, file_id=id, payload=data)
    payload = []
    for indicator in indicators:
        item = GetIndicator.model_validate(indicator).model_dump()
        item["preview_region_count"] = len(indicator.table.regions)
        item["preview_year_count"] = len(indicator.table.years)
        payload.append(UploadIndicatorResponse(**item))
    return UploadIndicatorsResponse(indicators=payload, created_count=len(payload))


@router.delete("/files/{id}")
async def delete_indicator_file(id: str = Path(...), user=Depends(get_current_user)):
    await IndicatorLogic.delete_file_for_user(user, id)
    return {"message": f"Файл с id={id} удалён"}


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


@router.post("/preview", response_model=IndicatorFilePreviewResponse)
async def preview_indicator_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    sheets = await IndicatorLogic.preview_file(file=file)
    years: list[str] = []
    for sheet in sheets:
        for year in sheet["years"]:
            if year not in years:
                years.append(year)
    return IndicatorFilePreviewResponse(
        sheets=[IndicatorFilePreviewSheet(**sheet) for sheet in sheets],
        years=years,
    )


@router.post("/upload_many", response_model=UploadIndicatorsResponse)
async def upload_indicators(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(default=None),
    split_by_year: bool = Form(default=False),
    years: str | None = Form(default=None),
    user=Depends(get_current_user),
):
    selected_years = [
        year.strip()
        for year in (years or "").split(",")
        if year.strip()
    ] or None
    indicators = await IndicatorLogic.upload_many(
        user=user,
        file=file,
        name=name,
        description=description,
        split_by_year=split_by_year,
        years=selected_years,
    )
    payload = []
    for indicator in indicators:
        item = GetIndicator.model_validate(indicator).model_dump()
        item["preview_region_count"] = len(indicator.table.regions)
        item["preview_year_count"] = len(indicator.table.years)
        payload.append(UploadIndicatorResponse(**item))
    return UploadIndicatorsResponse(indicators=payload, created_count=len(payload))


@router.put("/{id}", response_model=GetIndicator)
async def update_indicator(data: UpdateIndicator, id: str = Path(...), user=Depends(get_current_user)):
    return await IndicatorLogic.update_for_user(user, id, data)


@router.delete("/{id}")
async def delete_indicator(id: str = Path(...), user=Depends(get_current_user)):
    await IndicatorLogic.delete_for_user(user, id)
    return {"message": f"Показатель с id={id} успешно удалён"}
