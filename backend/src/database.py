from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import get_mongo_uri
from src.models_registry import *

async def init_db():
    client = AsyncIOMotorClient(get_mongo_uri())
    db = client.get_default_database()
    await init_beanie(
        database=db,
        document_models=[User, Project, Level, Module, Function, Indicator]
    )