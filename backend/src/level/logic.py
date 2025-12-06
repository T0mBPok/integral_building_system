from src.level.dao import LevelDAO
from src.project.dao import ProjectDAO
from src.project.schemas import GetProject

class LevelLogic(LevelDAO):
    @classmethod
    async def level_add(cls, **data):
        project_id = data.pop('project_id')
        project = await ProjectDAO.get_one_or_none_by_id(project_id)
        data['project'] = project
        return await super().add(**data)
    
    @classmethod
    async def get(cls, **filter_by):
        levels = await cls.model.find(**filter_by).to_list()
        for level in levels:
            if level.project:
                proj = await level.project.fetch()
                level.project = GetProject.model_validate(proj)
        return levels

    @classmethod
    async def get_one_or_none_by_id(cls, id: str):
        level = await cls.model.get(id)
        if level and level.project:
            proj = await level.project.fetch()
            level.project = GetProject.model_validate(proj)
        return level