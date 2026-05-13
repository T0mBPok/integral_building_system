from pymongo import AsyncMongoClient
from beanie import init_beanie
from src.config import get_mongo_uri
from src.models_registry import *


async def _deduplicate_collection_by_user_and_name(db, collection_name: str) -> None:
    collection = db[collection_name]
    pipeline = [
        {
            "$group": {
                "_id": {"user": "$user", "name": "$name"},
                "ids": {"$push": "$_id"},
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
    ]

    duplicates = await collection.aggregate(pipeline)
    async for duplicate in duplicates:
        ids = duplicate["ids"]
        base_name = duplicate["_id"].get("name") or "unnamed"

        for index, document_id in enumerate(ids[1:], start=2):
            new_name = f"{base_name}__dup_{index}"
            suffix = index

            while await collection.find_one(
                {
                    "user": duplicate["_id"]["user"],
                    "name": new_name,
                    "_id": {"$ne": document_id},
                }
            ):
                suffix += 1
                new_name = f"{base_name}__dup_{suffix}"

            await collection.update_one(
                {"_id": document_id},
                {"$set": {"name": new_name}},
            )


async def init_db():
    client = AsyncMongoClient(get_mongo_uri())
    db = client.get_default_database()
    await _deduplicate_collection_by_user_and_name(db, "indicators")
    await _deduplicate_collection_by_user_and_name(db, "indicator_files")
    await _deduplicate_collection_by_user_and_name(db, "projects")
    await init_beanie(
        database=db,
        document_models=[User, Project, Level, Module, Function, Indicator, IndicatorFile]
    )
