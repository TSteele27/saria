import json
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
_REASON = "reason"


class DocumentNotFoundException(Exception):
    pass


class CommitFailedException:
    pass


class MessagesDataAccess(Module):
    def __init__(self, config: Config, mongo_client: MongoClient):
        self.messages_collection = mongo_client.client[config.mongo.database][
            _MESSAGES_COLLECTION
        ]
        self.payloads_collection = mongo_client.client[config.mongo.database][
            _PAYLOADS_COLLECTIONS
        ]

    def _find_one_and_update(self, query: dict, to_values: dict) -> dict:
        message = self.messages_collection.find_one_and_update(
            query,
            {"$set": to_values},
            return_document=ReturnDocument.AFTER,
        )
        if message is None:
            raise DocumentNotFoundException(
                f"Failed to update object values. No value matching: {json.dumps(query)}"
            )
        return message

    def create_payload(self, payload: Payload) -> Payload:
        result = self.payloads_collection.insert_one(payload)
        return Payload(
            **self.payloads_collection.find_one(
                {
                    _MONGO_ID: result.inserted_id,
                }
            )
        )

    def create_message(self, message: Message) -> Message:
        message_dict = message.dict(
            by_alias=True,
        )
        del message_dict["_id"]
        result = self.messages_collection.insert_one(message_dict)
        created = self.messages_collection.find_one({_MONGO_ID: result.inserted_id})
        return Message(**created)

    def commit_failure(self, message: Message, reason: str):
        try:
            Message(
                **self._find_one_and_update(
                    {
                        _MONGO_ID: ObjectId(message.id),
                    },
                    {
                        _STATUS: MessageStatus.FAILED,
                        _REASON: reason,
                    },
                )
            )
        except DocumentNotFoundException as e:
            raise CommitFailedException(
                f"Failed to commit failure for message with id: {str(message.id)}"
            ) from e

    def commit_success(self, message: Message) -> None:
        try:
            Message(
                **self._find_one_and_update(
                    {
                        _MONGO_ID: ObjectId(message.id),
                    },
                    {
                        _STATUS: MessageStatus.PROCESSED,
                    },
                )
            )
        except DocumentNotFoundException as e:
            raise CommitFailedException(
                f"Failed to consume message with id: {str(message.id)}"
            ) from e

    def get_message_for_processing(self, message: Message) -> Message | None:
        try:
            message = self._find_one_and_update(
                {
                    _MONGO_ID: ObjectId(message.id),
                    _STATUS: MessageStatus.CREATED,
                },
                {
                    _STATUS: MessageStatus.PROCESSING,
                },
            )
            if message:
                payload = message["payload"]
                if message["payload_id"]:
                    payload = self.payloads_collection.find_one(
                        {
                            _MONGO_ID: ObjectId(message.payload_id),
                        }
                    )
                return Message(
                    **{
                        **message,
                        "payload": payload,
                    }
                )

        except DocumentNotFoundException as e:
            raise DocumentNotFoundException(
                f"Failed to find message for processing with id {str(message.id)}"
            ) from e


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

    def commit_message(self, message: Message) -> Message:
        return self.data_access.commit_success(message)

    def commit_failure(self, message: Message, reason: str):
        return self.data_access.commit_failure(message, reason)


class MessagesService(Module):
    def __init__(self, messages_repository: MessagesRepository):
        self.repository = messages_repository

    def create_payload(self, payload: Payload) -> Payload:
        return self.repository.create_payload(payload)

    def create_message(self, message: Message) -> Message:
        return self.repository.create_message(message)

    def get_message_for_processing(self, message: Message) -> Message | None:
        return self.repository.get_message_for_processing(message)

    def commit_message(self, message: Message) -> Message:
        return self.repository.commit_message(message)

    def commit_failure(self, message: Message, reason: str):
        return self.repository.commit_failure(message, reason)
