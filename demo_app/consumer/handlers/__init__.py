from saria.messaging.consumer.message_handler import MessageHandler
from demo_app.models import PetCommands


class CreatedHandler(MessageHandler):
    name: PetCommands.CREATE_PET

    def process_message(self, message: Message):
        print(f"Processing {self.name}")
        pass
