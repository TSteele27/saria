import os
import boto3
from saria.app import Module, Config
from saria.messaging import Message, Payload, MessageType
from saria.messaging.models import CommandTypes
from saria.messaging.service import MessagesService


class Producer(Module):
    def publish_message(self, message: Message):
        pass

    def publish_payload(self, payload: Payload):
        pass


class SNSProducer(Module):
    def __init__(self, config: Config, messages_service: MessagesService):
        self.config = config
        # self.topic_arn = config.producer.topic_arn
        self.sns_client = boto3.client(
            "sns",
            endpoint_url=os.environ["LOCALSTACK_ENDPOINT_URL"],
        )
        self.command_topic = "arn:aws:sns:us-east-1:000000000000:pets-commands"
        self.events_topic = "arn:aws:sns:us-east-1:000000000000:pets-events"
        self.messages_service = messages_service

    def publish_message(self, message: Message):
        """Publishes the message as is without saving a payload to the database."""
        topic = self.events_topic
        if isinstance(message.type, CommandTypes):
            topic = self.command_topic
        msg = self._serialize_message(message)
        print("JSON")
        print(msg.model_dump_json())
        self.sns_client.publish(
            TopicArn=topic,
            Message=msg.model_dump_json(),
        )
        return message

    def publish_payload(self, payload: Payload, message_type: MessageType):
        """Publishes a message serializing the payload into a store db before passing the id instead of the whole thing."""
        pd = self._serialize_payload(payload)
        self.publish_message(
            Message(
                payload_id=pd.id,
                type=message_type,
            )
        )

    def _serialize_message(self, message: Message) -> Message:
        ## TODO Save message to database
        return self.messages_service.create_message(message)

    def _serialize_payload(self, payload: Payload) -> Payload:
        ## TODO save payload to database
        return self.messages_service.create_payload(payload)
