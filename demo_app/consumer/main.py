from saria.app import Bundle
from saria.messaging.consumer import bundle as consumer_bundle

# from .message_handlers import Handlers


def run():
    app = Bundle().extend(**consumer_bundle).bootstrap()
    app.manifest.consumer.start()
