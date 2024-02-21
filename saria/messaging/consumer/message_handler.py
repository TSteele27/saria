from typing import TypeVar, Generic
from saria.app import Module
from saria.messaging.models import Message
from .message_handlers import MessageHandlers

T = TypeVar("T")


class MessageHandler(Module, Generic[T]):
    name: str

    def __init__(self, handlers: MessageHandlers):
        handlers.register(self)

    def process_message(self, message: Message):
        pass
