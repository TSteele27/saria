from demo_app.data_access import PetsRepository
from saria.http.server import Route
from demo_app.models import Pet
from http import HTTPMethod


class GetPet(Route):
    """Gets a pet."""

    path = "/pets/:id"
    method = HTTPMethod.GET

    def __init__(self, pets_repository: PetsRepository):
        self.pets_repository = pets_repository

    def handler(self, id: str):
        """Returns the pet with a given id."""
        return self.pets_repository.get(id)
