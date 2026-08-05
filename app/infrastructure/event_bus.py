import inspect
import logging
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from threading import Lock

from app.interfaces.event_bus import EventBus
from blinker import Signal
import asyncio

# event bus that makes use of a hybrid approach to handle sync handlers, async handlers, and CPU bound handlers
cpu_bound_handlers = []
class SimpleEventBus(EventBus):
    def __init__(self):
        self._emitter: dict[type, Signal] = {}
        self._logger = logging.getLogger(__name__)
        self._thread_executor = ThreadPoolExecutor(max_workers=8)
        self._process_executor = ProcessPoolExecutor(max_workers=2)
        self._pending_futures: set[Future] = set()
        self._pending_lock = Lock()

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
                        self._track_future(
                            self._process_executor.submit(
                                self._safe_handle,
                                receiver,
                                event,
                            )
                        )
                    else:
                        self._track_future(
                            self._thread_executor.submit(
                                self._safe_handle,
                                receiver,
                                event,
                            )
                        )

    def _track_future(self, future: Future) -> None:
        with self._pending_lock:
            self._pending_futures.add(future)
        future.add_done_callback(self._remove_pending_future)

    def _remove_pending_future(self, future: Future) -> None:
        with self._pending_lock:
            self._pending_futures.discard(future)

    def drain(self) -> None:
        while True:
            with self._pending_lock:
                pending = tuple(self._pending_futures)
            if not pending:
                return
            for future in pending:
                future.result()

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
