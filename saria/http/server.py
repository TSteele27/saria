from abc import ABC, abstractmethod
from http import HTTPMethod, HTTPStatus
from fastapi import FastAPI
from typing import List
from saria.app import Module


class Route(Module, ABC):
    method: HTTPMethod.GET
    default_status: HTTPStatus.OK
    path: str

    @abstractmethod
    def handler():
        pass


class HttpServer(Module):
    def __init__(self, routes: List[Route]):
        self.routes = routes
        self.app = FastAPI()
        print(self.app)
        self.start()

    def start(self):
        for route in self.routes:
            print(f"Adding {route.method} {route.handler} {route.path}")
            getattr(self.app, route.method.lower())(route.path)(route.handler)
