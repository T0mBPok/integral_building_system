
from pydantic import BaseModel, field_validator
from bson import ObjectId

class MongoBaseModel(BaseModel):
    id: str | None = None

    @field_validator("id", mode="before")
    def objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }