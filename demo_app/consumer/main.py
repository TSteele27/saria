from saria.app import Bundle
from saria.messaging.consumer import bundle as consumer_bundle

# from .message_handlers import Handlers


def run():
    print("Starting consumer...")
    app = Bundle().extend(**consumer_bundle).bootstrap()
    app.manifest.consumer.start()


if __name__ == "__main__":
    run()
