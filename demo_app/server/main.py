from dotenv import load_dotenv

load_dotenv()
from saria.app import Bundle
from saria.http import bundle as http_bundle
from .routes import routes
from saria.messaging import producer_bundle, SetupLocalStack

app = (
    Bundle(
        routes=routes,
        setup_localstack=SetupLocalStack,
    )
    .extend(**http_bundle)
    .extend(**producer_bundle)
    .bootstrap()
    .manifest.server.app
)
