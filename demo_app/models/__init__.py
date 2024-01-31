from .pet import Pet
from saria.messaging.models import CommandTypes


class PetCommands(CommandTypes):
    CREATE_PET = "pet.create"
    UPDATE_PET = "pet.update"
