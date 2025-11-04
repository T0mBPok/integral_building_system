from fastapi import APIRouter, Depends, Path
from src.function.schemas import GetFunction, AddFunction, UpdateFunction
from src.function.rb import RBFunction
from src.function.logic import FunctionLogic

router = APIRouter(prefix="/function", tags=["Работа с функциями"])

@router.get("/", summary="Получить список функций", response_model=list[GetFunction])
async def get_functions(request_body: RBFunction = Depends()):
    return await FunctionLogic.get(**request_body.to_dict())

@router.get("/{id}", summary="Получить функцию по ID", response_model=GetFunction)
async def get_function_by_id(id: int = Path(..., gt=0)):
    return await FunctionLogic.get_one_or_none_by_id(id=id)

@router.post("/", summary="Добавить функцию", response_model=GetFunction)
async def add_function(form_data: AddFunction = Depends(AddFunction.as_form)):
    return await FunctionLogic.add(**form_data.model_dump())

@router.delete("/{id}", summary="Удалить функцию")
async def delete_function(id: int = Path(..., gt=0)):
    await FunctionLogic.delete(id=id)
    return {"message": f"Функция с id={id} успешно удалена!"}

@router.put("/{id}", summary="Обновить функцию", response_model=GetFunction)
async def update_function(function: UpdateFunction, id: int = Path(..., gt=0)):
    new_data = function.model_dump(exclude_unset=True)
    await FunctionLogic.update_function(id=id, **new_data)
    return new_data