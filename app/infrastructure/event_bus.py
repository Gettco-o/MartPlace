import logging
from typing import Any, Iterable, Callable

from app.interfaces.event_bus import EventBus

from blinker import NamedSignal, Signal, signal 

from concurrent.futures import ThreadPoolExecutor

#simple event bus implementation
""" 
class ISimpleEventBus(EventBus):
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

 """
# event bus with blinker library
"""
class SimpleEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, event_type: type, handler: Callable[[Any], None]):
        emitter_obj = self._emitter.get(event_type)
        if emitter_obj is None:
            emitter_obj = Signal(event_type.__name__)
            self._emitter[event_type] = emitter_obj
        emitter_obj.connect(handler, weak=False)
        
        
    def publish(self, events: Iterable[Any]):
        for event in events:
            event_type = type(event)
            try:
                emmiter_obj = self._emitter.get(event_type)
                emmiter_obj.send(event)
            except Exception:
                self._logger.exception("Error while handling event %s", type(event))
"""
# event bus with threadpool
class SimpleEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=10)

    def register(self, event_type: type, handler: Callable[[Any], None]):
        emitter_obj = self._emitter.get(event_type)
        if emitter_obj is None:
            emitter_obj = Signal(event_type.__name__)
            self._emitter[event_type] = emitter_obj
        emitter_obj.connect(handler, weak=False)
        
        
    def publish(self, events: Iterable[Any]):
        for event in events:
            event_type = type(event)
            emitter_obj = self._emitter.get(event_type)
            if emitter_obj:
                self._executor.submit(self._safe_send, emitter_obj, event)
            

    def _safe_send(self, emitter_obj: Signal, event):
        try:
            emitter_obj.send(event)
        except Exception:
            self._logger.exception(
                "Error while handling event %s",
                type(event).__name__,
            ) 

# TODO: async event bus implementation using asyncio and async signals
"""
class AsyncEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, event_type: type, handler: Callable[[Any], None]):
        emitter_obj = self._emitter.get(event_type)
        if emitter_obj is None:
            emitter_obj = Signal(event_type.__name__)
            self._emitter[event_type] = emitter_obj
        emitter_obj.connect(handler, weak=False)
        
        
    async def publish(self, events: Iterable[Any]):
        for event in events:
            event_type = type(event)
            emitter_obj = self._emitter.get(event_type)
            if emitter_obj:
                await self._safe_send(emitter_obj, event)

    async def _safe_send(self, emitter_obj: Signal, event):
        try:
            emitter_obj.send(event)
        except Exception:
            self._logger.exception(
                "Error while handling event %s",
                type(event).__name__,
            )

"""