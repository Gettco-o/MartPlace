class EventBus:

    def __init__(self):
        self._handlers = {}

    def register(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, events):
        for event in events:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                handler(event)
