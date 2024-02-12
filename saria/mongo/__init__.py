from saria.app import Module, Config
from pymongo import MongoClient as PyMongoClient, ReturnDocument
import json


class MongoClient(Module):
    def __init__(self, config: Config):
        host = config.mongo.host
        self.client = PyMongoClient(host)
