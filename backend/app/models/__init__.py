# Import all models here so SQLAlchemy knows about them.
# When you implement a new model, add its import here.

from app.models.user import User                       # noqa: F401
from app.models.trip import Trip                       # noqa: F401
from app.models.itinerary import Itinerary             # noqa: F401
from app.models.trip_hotel import TripHotel             # noqa: F401
from app.models.trip_attraction import TripAttraction   # noqa: F401
from app.models.agent_log import AgentLog               # noqa: F401
