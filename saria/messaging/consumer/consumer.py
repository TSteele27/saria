import json
import os
import sys
from saria.messaging.models import Message
from saria.messaging.consumer.message_handlers import MessageHandlers
from saria.app import Module, Config
from pyee import EventEmitter

import boto3

from saria.messaging.service import MessagesService

import signal


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

    def _mount_handlers(self):
        for handler in self.message_handlers:
            self.on(handler.message_type, handler.process_message)

    def _get_message_for_processing(self, from_message: Message) -> Message:
        # retrieve message and mark is as processing
        print(from_message)
        return self.messages_service.get_message_for_processing(from_message)

    def start(self):
        print("::Consumer Starting::")
        super().start()
        print("::Consumer Started::")
        while True:
            print(self.running)
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=5 * 60,
                WaitTimeSeconds=30,
            )
            print(response)
            messages = response.get("Messages", [])
            if messages:
                print("Got messages...")
                message = messages[0]
                print(message)
                body = json.loads(messages[0]["Body"])
                print("XXX BODY")
                print(body)
                msg = json.loads(body["Message"])
                print(msg)
                print(type(msg))
                # print(msg["type"])
                # message = self._get_message_for_processing(
                #     Message(
                #         id=msg.id,
                #         type=msg["type"],
                #         payload=msg["payload"],
                #     )
                # )
                # TODO
                # if message.status is not MessageStatus.CREATED:
                print("Message found in the queue:", message)
                self.sqs_client.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=messages[0]["ReceiptHandle"],
                )
                print("Deleted...")
                sys.stdout.flush()
