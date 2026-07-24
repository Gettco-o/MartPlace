import inspect
import logging
from typing import Any, Iterable, Callable

from app.interfaces.event_bus import EventBus

from blinker import Signal

from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ProcessPoolExecutor

import asyncio

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
"""
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
"""

# events with threadpool and dedicated workers for handlers (not just events)
# so each handler is dedicated to a worker and can run concurrently with other handlers within same event type
"""
class SimpleEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=10)

    def register(self, event_type: type, handler):
        emitter_obj = self._emitter.get(event_type)

        if emitter_obj is None:
            emitter_obj = Signal(event_type.__name__)
            self._emitter[event_type] = emitter_obj

        emitter_obj.connect(handler, weak=False)


    def publish(self, events):
        for event in events:
            event_type = type(event)
            emitter_obj = self._emitter.get(event_type)

            if emitter_obj:
                for receiver in emitter_obj.receivers_for(event):
                    self._executor.submit(
                        self._safe_handle,
                        receiver,
                        event
                    )


    def _safe_handle(self, handler, event):
        try:
            handler(event)
        except Exception:
            self._logger.exception(
                "Error handling event %s",
                type(event).__name__
            )
"""
# event bus that makes use of a hybrid approach to handle sync handlers, async handlers, and CPU bound handlers
cpu_bound_handlers = []
class SimpleEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)
        self._thread_executor = ThreadPoolExecutor(max_workers=8)
        self._process_executor = ProcessPoolExecutor(max_workers=2)

    def register(self, event_type: type, handler):
        emitter_obj = self._emitter.get(event_type)

        if emitter_obj is None:
            emitter_obj = Signal(event_type.__name__)
            self._emitter[event_type] = emitter_obj

        emitter_obj.connect(handler, weak=False)


    def publish(self, events):
        for event in events:
            event_type = type(event)
            emitter_obj = self._emitter.get(event_type)

            if emitter_obj:
                for receiver in emitter_obj.receivers_for(event):
                    if inspect.iscoroutinefunction(receiver):
                        asyncio.create_task(
                            self._safe_async_handle(receiver, event)
                        )
                    elif receiver in cpu_bound_handlers:
                        self._process_executor.submit(
                            self._safe_handle,
                            receiver,
                            event
                        )
                    else:
                        self._thread_executor.submit(
                            self._safe_handle,
                            receiver,
                            event
                        )


    def _safe_handle(self, handler, event):
        try:
            handler(event)
        except Exception:
            self._logger.exception(
                "Error handling event %s",
                type(event).__name__
            )
    async def _safe_async_handle(self, handler, event):
        try:
            await handler(event)
        except Exception:
            self._logger.exception(
                "Error handling event %s",
                type(event).__name__
            )