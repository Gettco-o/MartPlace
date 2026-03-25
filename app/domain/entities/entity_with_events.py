from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntityWithEvents:
    _events: list[Any] = field(default_factory=list, init=False, repr=False)

    @property
    def events(self) -> list[Any]:
        return self._events

    def record_event(self, event: Any) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()
