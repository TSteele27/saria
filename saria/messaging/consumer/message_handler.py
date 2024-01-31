from enum import StrEnum
from typing import Optional
from saria.app import Module
from .message_handlers import MessageHandlers


class Payload:
    pass


class MessageType(StrEnum):
    pass


class Message:
    type: MessageType
    payload: Payload
    payload_id: Optional[str]
    message_id: str
    pass


class MessageHandler(Module):
    def __init__(self, handlers: MessageHandlers):
        handlers.register(self)

    def process_message(self, message: Message):
        pass
