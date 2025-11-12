from fastapi import APIRouter, Depends, HTTPException, Path
from src.level.schemas import GetLevel, AddLevel, UpdateLevel
from src.level.rb import RBLevel
from src.level.logic import LevelLogic

router = APIRouter(prefix="/level", tags=["Работа с уровнями"])

@router.get("/", response_model=list[GetLevel])
async def get_levels(request: RBLevel = Depends()):
    return await LevelLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetLevel)
async def get_level_by_id(id: str):
    level = await LevelLogic.get_one_or_none_by_id(id=id)
    if not level:
        raise HTTPException(status_code=404, detail="Уровень не найден")
    return level

@router.post("/", response_model=GetLevel)
async def add_level(data: AddLevel):
    return await LevelLogic.add(**data.model_dump())

@router.put("/{id}", response_model=GetLevel)
async def update_level(id: str, data: UpdateLevel):
    await LevelLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await LevelLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_level(id: str):
    await LevelLogic.delete(id=id)
    return {"message": f"Уровень с id={id} успешно удалён"}