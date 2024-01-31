import boto3
from botocore.exceptions import ClientError
from saria.app import Module
from enum import StrEnum
from saria.app.config import Config
import os


class Environment(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SetupLocalStack(Module):
    def __init__(self, config: Config):
        if config.app.env != Environment.LOCAL:
            return
        self.sns_client = boto3.client(
            "sns",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        )
        self.sqs_client = boto3.client(
            "sqs",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        )
        self.topics = []
        self.topics.append(self.create_topic(f"{config.app.name}-commands"))
        self.topics.append(self.create_topic(f"{config.app.name}-events"))
        self.queue_url = self.create_queue(f"{config.app.name}-queue")

        self.subscribe_queue_to_topics()

    def create_topic(self, topic_name):
        try:
            response = self.sns_client.create_topic(Name=topic_name)
            topic_arn = response["TopicArn"]
            print(f"Created topic '{topic_name}' with ARN: {topic_arn}")
            return topic_arn
        except ClientError as e:
            if e.response["Error"]["Code"] == "TopicNameAlreadyExists":
                print(f"Topic '{topic_name}' already exists.")
                return self.sns_client.list_topics(TopicName=topic_name)["Topics"][0][
                    "TopicArn"
                ]
            else:
                raise

    def create_queue(self, queue_name):
        try:
            response = self.sqs_client.create_queue(QueueName=queue_name)
            queue_url = response["QueueUrl"]
            print(f"Created queue '{queue_name}' with URL: {queue_url}")
            queue_arn = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url, AttributeNames=["QueueArn"]
            )["Attributes"]["QueueArn"]
            print(f"Queue ARN: {queue_arn}")
            return queue_arn
        except ClientError as e:
            if e.response["Error"]["Code"] == "QueueAlreadyExists":
                print(f"Queue '{queue_name}' already exists.")
                existing_queue_url = self.sqs_client.get_queue_url(
                    QueueName=queue_name
                )["QueueUrl"]
                print(f"Queue URL:{queue_url}")
                existing_queue_arn = self.sqs_client.get_queue_attributes(
                    QueueUrl=existing_queue_url, AttributeNames=["QueueArn"]
                )["Attributes"]["QueueArn"]
                print(f"Queue ARN: {existing_queue_arn}")
                return existing_queue_arn
            else:
                raise e

    def subscribe_queue_to_topics(self):
        for topic in self.topics:
            self.sns_client.subscribe(
                TopicArn=topic,
                Protocol="sqs",
                Endpoint=self.queue_url,
            )
            print(f"Subscribed queue to topic: '{topic}'")
