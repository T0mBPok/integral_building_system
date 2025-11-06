from src.project.dao import ProjectDAO
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.database import async_session
from src.project.model import Project

class ProjectLogic(ProjectDAO):
    @staticmethod
    async def get(**filters):
        async with async_session() as session:
            query = select(Project).options(selectinload(Project.levels))
            for key, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(Project, key) == value)
            result = await session.execute(query)
            return result.scalars().unique().all()

    @staticmethod
    async def get_one_or_none_by_id(id: int):
        async with async_session() as session:
            query = select(Project).options(selectinload(Project.levels)).filter(Project.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
