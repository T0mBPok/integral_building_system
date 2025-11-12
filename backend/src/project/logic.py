from src.project.dao import ProjectDAO
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.database import with_session
from src.project.model import Project

class ProjectLogic(ProjectDAO):
    ...
