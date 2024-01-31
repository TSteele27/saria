from saria.data_access import BaseRepository
from demo_app.models import Pet


class PetsRepository(BaseRepository[Pet]):
    """Repository layer for pets resource."""
