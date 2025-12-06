from beanie import Link
from src.indicator.dao import IndicatorDAO
from src.user.model import User

class IndicatorLogic(IndicatorDAO):
    @classmethod
    async def indicator_add(cls, user: User, data: dict):
        data["user"] = Link(user)
        return await super().add(**data)
