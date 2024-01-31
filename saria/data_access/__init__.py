import datetime
from typing import Generic, TypeVar
from saria.app import Module
from saria.models import Resource, ListResults

T = TypeVar("T", bound=Resource)


class DataAccess(Module, Generic[T]):
    def get(self, id: str) -> T:
        pass

    def create(self, resource: T) -> T:
        pass

    def update(self, resource: T) -> T:
        pass

    def list(self, query: dict) -> ListResults[T]:
        pass


class BaseRepository(Module, Generic[T]):
    def __init__(self, data_access: DataAccess):
        self.data_access = data_access

    def get(self, id: str) -> T:
        return self.data_access.get(id)

    def create(self, resource: T) -> T:
        return self.data_access.create(resource)

    def update(self, resource: T) -> T:
        resource.updated_date = datetime.now()
        return self.data_access.update(resource)

    def list(self, query: dict) -> ListResults[T]:
        return self.data_access.list(query)
