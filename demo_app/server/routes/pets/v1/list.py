from demo_app.models.pet import PetsListResults
from saria.http.server import Route
from demo_app.models import Pet
from http import HTTPMethod


class ListPets(Route):
    """Lists pets matching query."""

    path = "/pets"
    method = HTTPMethod.GET

    def handler(self, name: str, age: int):
        return PetsListResults(count=1, results=[Pet(name=name, age=age)])
