from saria.http.server import Route
from demo_app.models import Pet, PetCommands
from http import HTTPMethod
from saria.messaging import SNSProducer, Message
from saria.messaging.models import Payload


class PostPet(Route):
    """Create Pet."""

    path = "/pets"
    method = HTTPMethod.POST

    def __init__(self, producer: SNSProducer):
        self.producer = producer

    def handler(self, pet: Pet):
        self.producer.publish_message(
            Message(
                type=PetCommands.CREATE_PET,
                payload=Payload(
                    value=pet,
                ),
            )
        )
        return Pet(**pet.model_dump())
