from fastapi import HTTPException, status
from beanie import Document
from typing import Type, TypeVar, Optional, List, Any

T = TypeVar("T", bound=Document)

class BaseDAO:
    model: Type[T] = None

    @classmethod
    async def get(cls, **filter_by) -> List[T]:
        return await cls.model.find(filter_by).to_list()

    @classmethod
    async def get_except_current(cls, current_id: Any) -> List[T]:
        return await cls.model.find(cls.model.id != current_id).to_list()

    @classmethod
    async def get_one_or_none_by_id(cls, id: Any) -> Optional[T]:
        return await cls.model.get(id)

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> Optional[T]:
        return await cls.model.find_one(filter_by)

    @classmethod
    async def add(cls, **values) -> T:
        new_obj = cls.model(**values)
        try:
            await new_obj.insert()
            return new_obj
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @classmethod
    async def delete(cls, id: Any) -> int:
        obj = await cls.model.get(id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await obj.delete()
        return 1

    @classmethod
    async def update(cls, id: Any, **values) -> int:
        obj = await cls.model.get(id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await obj.set(values)
        return 1