from app.infrastructure.db import Database
from app.infrastructure.event_bus import SimpleEventBus
from quart_schema import QuartSchema

db = Database()
event_bus = SimpleEventBus()
qs = QuartSchema()
