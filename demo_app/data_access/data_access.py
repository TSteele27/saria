from saria.data_access import DataAccess
from demo_app.models import Pet


class PetsDataAccess(DataAccess[Pet]):
    """Repository layer for pets resource."""
