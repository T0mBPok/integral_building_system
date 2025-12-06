from fastapi import APIRouter, Depends, HTTPException, Path
from src.function.schemas import GetFunction, AddFunction, UpdateFunction
from src.function.rb import RBFunction
from src.function.logic import FunctionLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix="/function", tags=["Работа с функциями"])

@router.get("/", response_model=list[GetFunction])
async def get_functions(request: RBFunction = Depends(), user=Depends(get_current_user)):
    return await FunctionLogic.get(**request.to_dict())

@router.get("/{id}", response_model=GetFunction)
async def get_function_by_id(id: str = Path(...), user=Depends(get_current_user)):
    func = await FunctionLogic.get_one_or_none_by_id(id=id)
    if not func:
        raise HTTPException(status_code=404, detail="Функция не найдена")
    return func

@router.post("/", response_model=GetFunction)
async def add_function(data: AddFunction = Depends(AddFunction.as_form), user=Depends(get_current_user)):
    return await FunctionLogic.add(**data.model_dump())

@router.put("/{id}", response_model=GetFunction)
async def update_function(data: UpdateFunction, id: str = Path(...), user=Depends(get_current_user)):
    await FunctionLogic.update(id=id, **data.model_dump(exclude_unset=True))
    return await FunctionLogic.get_one_or_none_by_id(id=id)

@router.delete("/{id}")
async def delete_function(id: str = Path(...), user=Depends(get_current_user)):
    await FunctionLogic.delete(id=id)
    return {"message": f"Функция с id={id} успешно удалена"}
