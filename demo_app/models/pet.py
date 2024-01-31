from pydantic import BaseModel
from saria.models import ListResults


class Pet(BaseModel):
    name: str
    age: int


class PetsListResults(ListResults[Pet]):
    """Results of a list pets query."""
