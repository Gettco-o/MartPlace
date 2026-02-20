import logging
from typing import Any, Iterable, Callable

from app.interfaces.event_bus import EventBus


class SimpleEventBus(EventBus):
    """A simple in-memory event bus implementation.

    - Keeps a mapping of event type -> handlers
    - Calls each handler for published events
    - Catches and logs handler exceptions (best-effort delivery)
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, event_type: type, handler: Callable[[Any], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, events: Iterable[Any]) -> None:
        for event in events:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception:
                    # Don't let one failing handler stop the others.
                    self._logger.exception("Error while handling event %s", type(event))
