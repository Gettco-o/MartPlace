from abc import ABC, abstractmethod
from typing import Iterable, Callable, Any


class EventBus(ABC):
    """Abstract EventBus contract.

    Implementations must provide `register` and `publish` methods. Handlers
    are callables that accept a single event object.
    """

    @abstractmethod
    def register(self, event_type: type, handler: Callable[[Any], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def publish(self, events: Iterable[Any]) -> None:
        raise NotImplementedError