from fastapi import APIRouter, Depends, Path
from src.level.schemas import GetLevel, AddLevel, UpdateLevel
from src.level.rb import RBLevel
from src.level.logic import LevelLogic

router = APIRouter(prefix="/level", tags=["Работа с уровнями"])


@router.get("/", summary="Получить список уровней", response_model=list[GetLevel])
async def get_levels(request_body: RBLevel = Depends()):
    return await LevelLogic.get(**request_body.to_dict())


@router.get("/{id}", summary="Получить уровень по ID", response_model=GetLevel)
async def get_level_by_id(id: int = Path(..., gt=0)):
    return await LevelLogic.get_one_or_none_by_id(id=id)


@router.post("/", summary="Добавить уровень", response_model=GetLevel)
async def add_level(form_data: AddLevel = Depends(AddLevel.as_form)):
    return await LevelLogic.add(**form_data.model_dump())


@router.put("/{id}", summary="Обновить уровень", response_model=GetLevel)
async def update_level(level: UpdateLevel, id: int = Path(..., gt=0)):
    new_data = level.model_dump(exclude_unset=True)
    await LevelLogic.update(id=id, **new_data)
    return await LevelLogic.get_one_or_none_by_id(id=id)


@router.delete("/{id}", summary="Удалить уровень")
async def delete_level(id: int = Path(..., gt=0)):
    await LevelLogic.delete(id=id)
    return {"message": f"Уровень с id={id} успешно удалён!"}
