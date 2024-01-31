from saria.app import Bundle
from .consumer import SQSConsumer

bundle = Bundle(consumer=SQSConsumer)
