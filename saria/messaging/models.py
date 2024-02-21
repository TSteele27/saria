from typing import TypeVar, Generic, Optional
from enum import StrEnum
from saria.models import Field, Resource

T = TypeVar("T")


class MessageStatus(StrEnum):
    CREATED = "created"
    PROCESSING = "processing"
    FAILED = "failed"
    PROCESSED = "processed"


class MessageType(StrEnum):
    pass


class CommandTypes(MessageType):
    pass


class EventTypes(MessageType):
    pass


class Payload(Resource, Generic[T]):
    value: T = Field(description="The value for the payload.")


class Message(Resource, Generic[T]):
    status: MessageStatus = Field(
        description="The status of the message.",
        default=MessageStatus.CREATED,
    )
    type: MessageType | str = Field(description="The message type.")
    payload: Optional[T] = Field(
        None,
        description="The value encapsulated in the message.",
    )
    payload_id: Optional[str] = Field(
        None,
        description="The ID of the payload stored in the DB.",
    )
    status_reason: Optional[str] = Field(
        None,
        description="The reason for the failed status if the event fails.",
    )
    attempts: int = Field(
        0,
        description="The number of times this message has been processed.",
    )
