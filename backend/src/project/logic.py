from src.project.dao import ProjectDAO
from src.user.model import User
from beanie import Link

class ProjectLogic(ProjectDAO):
    @classmethod
    async def project_add(cls, user: User, **data):
        data["User"] = Link(user)
        return await super().add(**data)