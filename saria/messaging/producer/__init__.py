"""saria.producer"""
from saria.app.bundle import Bundle
from .producer import SNSProducer

bundle = Bundle(
    producer=SNSProducer,
)
