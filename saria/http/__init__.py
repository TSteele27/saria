from saria.app import Bundle
from .server import HttpServer

bundle = Bundle(
    server=HttpServer,
)
