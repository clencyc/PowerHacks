from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId

# Custom ObjectId type for Pydantic v2
class PydanticObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        def validate(v: Any) -> ObjectId:
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)

        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(validate),
            json_schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        return handler(core_schema.str_schema())


class ReportBase(BaseModel):
    encrypted_blob: str
    channel_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending") # pending, reviewed, resolved

class Report(ReportBase):
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)

class ReportCreate(ReportBase):
    pass

class ReportRead(ReportBase):
    id: PydanticObjectId

class AnalyticsData(BaseModel):
    date: datetime
    incident_count: int
    category: str
