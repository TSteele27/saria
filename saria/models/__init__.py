from datetime import datetime
from bson.objectid import InvalidId, ObjectId as BaseObjectId
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List

T = TypeVar("T")


class ObjectId(str):
    """ObjectId class for pydantic models."""

    @classmethod
    def validate(cls, value):
        """Validate given str value to check if good for being ObjectId."""
        try:
            return BaseObjectId(str(value)) if value is not None else None
        except InvalidId as e:
            raise ValueError("Not a valid ObjectId") from e

    @classmethod
    def __get_validators__(cls):
        yield cls.validate


class Model(BaseModel):
    pass


MONGO_ID = "_id"


class Resource(Model):
    id: ObjectId | None = Field(
        None,
        description="The ID of the resource.",
        alias=MONGO_ID,
    )
    created: datetime = Field(
        description="The time this message was created at",
        default_factory=datetime.now,
    )
    updated: datetime = Field(
        description="The last time the message was updated",
        default_factory=datetime.now,
    )


class ListResults(Model, Generic[T]):
    total_count: int = Field(
        description="A count for the total number of results.",
    )
    results: List[T] = Field(
        description="A list containing the results from the query."
    )
