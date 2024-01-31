import os
from saria.app import Module, Config
from pyee import EventEmitter

import boto3


class Consumer(EventEmitter, Module):
    running: bool

    def __ini__(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


class SQSConsumer(Consumer):
    def __init__(self, config: Config):
        self.sqs_client = boto3.client(
            "sqs",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        )
        self.queue_url = "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/pets-queue"
        self.config = config

    def start(self):
        super().start()
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
                print("Message found in the queue:", message)
                self.delete_message(message["ReceiptHandle"])
                print("Deleted...")
                return message
