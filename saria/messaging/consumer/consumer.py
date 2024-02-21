import json
import os
import sys
from saria.messaging.consumer.message_handler import MessageHandler
from saria.messaging.models import Message
from saria.messaging.consumer.message_handlers import MessageHandlers
from saria.app import Module, Config
from pyee import EventEmitter
import logging
import boto3

from saria.messaging.service import DocumentNotFoundException, MessagesService

import signal

logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler(sys.stdout)
_logger = logging.getLogger(__name__)
_logger.addHandler(handler)


class MessageHandlerNotFoundException(Exception):
    pass


class Consumer(EventEmitter, Module):
    running: bool

    def __init__(self):
        self.running = False
        signal.signal(signal.SIGINT, self.stop)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self.stop)

    def start(self):
        self.running = True

    def stop(self):
        print(f"Stopping consumer process.")
        self.running = False


class SQSConsumer(Consumer):
    def __init__(
        self,
        config: Config,
        message_handlers: MessageHandlers,
        messages_service: MessagesService,
    ):
        super().__init__()
        self.sqs_client = boto3.client(
            "sqs",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        )
        self.queue_url = "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/pets-queue"
        self.config = config
        self.message_handlers = message_handlers
        self.messages_service = messages_service

    def _get_message_for_processing(self, from_message: Message) -> Message:
        # retrieve message and mark is as processing
        return self.messages_service.get_message_for_processing(from_message)

    def _get_handler_for_message(self, message: Message) -> MessageHandler:
        handler = next(
            (
                handler
                for handler in self.message_handlers
                if handler.name == message.type
            ),
            None,
        )
        if handler is None:
            raise MessageHandlerNotFoundException(
                f"No Message handler registered with name {message.type}."
            )
        return handler

    def _commit_success(self, message: Message, reciept_handle: str) -> None:
        self.messages_service.commit_message(message)
        self._delete_message(reciept_handle)
        _logger.info(f"Consumed message {message.id}.")

    def _commit_failure(
        self, message: Message, failure_reason: str, reciept_handle: str
    ) -> None:
        self.messages_service.commit_failure(message, failure_reason)
        self._delete_message(reciept_handle)
        _logger.info(f"Deleted failed message {message.id}.")

    def _delete_message(self, reciept_handle: str):
        self.sqs_client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=reciept_handle,
        )

    def _apply_recovery_policies(to_message: Message) -> Message | None:
        pass

    def start(self):
        super().start()
        _logger.info("Starting consumer watch loop....")
        while self.running:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=5 * 60,
                WaitTimeSeconds=30,
            )
            messages = response.get("Messages", [])
            if messages:
                message = messages[0]
                body = json.loads(messages[0]["Body"])
                msg = json.loads(body["Message"])
                reciept_handle = messages[0]["ReceiptHandle"]
                try:
                    try:
                        message = self._get_message_for_processing(
                            Message(
                                id=msg["id"],
                                type=msg["type"],
                                payload=msg["payload"],
                            )
                        )
                    except DocumentNotFoundException as e:
                        # TODO look for if the message is in a different status
                        # If Not found make a message and set it to processing.
                        # apply timeout/retry policies.
                        _logger.warn(
                            f"No message found for processing with id {message.id}"
                        )
                        message = self._apply_recovery_policies(message)
                        if message is None:
                            # The message was consumed by the
                            continue
                    except Exception as e:
                        raise e
                    handler = self._get_handler_for_message(message)
                    _logger.info(f"Processing message {message.id}.")
                    handler.process_message(message)
                    self._commit_success(message, reciept_handle)
                except MessageHandlerNotFoundException as e:
                    _logger.exception(
                        f"Failed to find handler for message: {message.id}",
                    )
                    self._commit_failure(
                        message,
                        str(e),
                        reciept_handle,
                    )
                except Exception as e:
                    _logger.exception(
                        f"Unknown Error Occured: {str(e)} Message processsing failed"
                    )
                    try:
                        self._commit_failure(
                            message,
                            str(e),
                            reciept_handle,
                        )
                    except Exception as e:
                        _logger.exception(
                            f"Failed to update message failure status for message {str(message.id)}. Removing queue entry: {reciept_handle}"
                        )
                        self._delete_message(reciept_handle)
                    finally:
                        sys.stdout.flush()
                        continue
                finally:
                    sys.stdout.flush()
                    continue
