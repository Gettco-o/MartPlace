from app.infrastructure.db import Database
from app.infrastructure.event_bus import SimpleEventBus
from quart_schema import QuartSchema,Info

db = Database()
event_bus = SimpleEventBus()
qs = QuartSchema(
      info=Info(
            title="MartPlace",
            version="1.0.0",
      ),
      security=[{"BearerAuth": []}],
      security_schemes={
            "BearerAuth": {
                  "type": "http",
                  "scheme": "bearer",
                  "bearer_format": "JWT",
            }
      }
)
