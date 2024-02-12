from saria.app import Module, Config
from saria.data_access import DataAccess, BaseRepository
from saria.messaging.models import Message, MessageStatus, Payload
from saria.mongo import MongoClient, ReturnDocument
from saria.service import BaseService
from bson import ObjectId

_MESSAGE_ID = "message_id"
_STATUS = "status"
_MESSAGES_COLLECTION = "messages"
_PAYLOADS_COLLECTIONS = "payloads"

_MONGO_ID = "_id"


class MessagesDataAccess(Module):
    def __init__(self, config: Config, mongo_client: MongoClient):
        self.messages_collection = mongo_client.client[config.mongo.database][
            _MESSAGES_COLLECTION
        ]
        self.payloads_collection = mongo_client.client[config.mongo.database][
            _PAYLOADS_COLLECTIONS
        ]

    def create_payload(self, payload: Payload) -> Payload:
        result = self.payloads_collection.insert_one(payload)
        return Payload(
            **self.payloads_collection.find_one({_MONGO_ID: result.inserted_id})
        )

    def create_message(self, message: Message) -> Message:
        message_dict = message.dict(
            by_alias=True,
        )
        del message_dict["_id"]
        result = self.messages_collection.insert_one(message_dict)
        created = self.messages_collection.find_one({_MONGO_ID: result.inserted_id})
        print(created)
        return Message(**created)

    def get_message_for_processing(self, message: Message) -> Message | None:
        message = self.messages_collection.find_one_and_update(
            {
                _MONGO_ID: ObjectId(message.id),
                _STATUS: MessageStatus.CREATED,
            },
            {
                "$set": {
                    _STATUS: MessageStatus.PROCESSING,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        if message:
            payload = message.payload
            if message.payload_id:
                payload = self.payloads_collection.find_one(
                    {_MONGO_ID: ObjectId(message.payload_id)}
                )
            return Message(**{**message, "payload": payload})
        # TODO look for if the message is in a different status
        # If Not found make a message and set it to processing.


class MessagesRepository(Module):
    def __init__(self, messaging_data_access: MessagesDataAccess):
        self.data_access = messaging_data_access
        print(self.data_access)

    def create_payload(self, payload: Payload) -> Payload:
        return self.data_access.create_payload(payload)

    def create_message(self, message: Message) -> Message:
        return self.data_access.create_message(message)

    def get_message_for_processing(self, message: Message) -> Message | None:
        return self.data_access.get_message_for_processing(message)


class MessagesService(Module):
    def __init__(self, messages_repository: MessagesRepository):
        self.repository = messages_repository

    def create_payload(self, payload: Payload) -> Payload:
        return self.repository.create_payload(payload)

    def create_message(self, message: Message) -> Message:
        return self.repository.create_message(message)

    def get_message_for_processing(self, message: Message) -> Message | None:
        return self.repository.get_message_for_processing(message)
