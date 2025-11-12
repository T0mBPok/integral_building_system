from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import get_mongo_uri
from src.user.model import User
from src.project.model import Project
from src.level.model import Level
from src.module.model import Module
from src.function.model import Function
from src.indicator.model import Indicator

async def init_db():
    client = AsyncIOMotorClient(get_mongo_uri())
    db = client.get_default_database()
    await init_beanie(
        database=db,
        document_models=[User, Project, Level, Module, Function, Indicator]
    )