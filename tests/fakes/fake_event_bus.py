from app.infrastucture.event_bus import SimpleEventBus


class FakeEventBus(SimpleEventBus):
    """A test-friendly EventBus that records published events.

    Subclassing the production `SimpleEventBus` gives us the concrete
    register/publish implementation for handler dispatch while allowing
    the fake to record published events for assertions.
    """

    def __init__(self):
        super().__init__()
        self.published_events = []

    def publish(self, events):
        for event in events:
            self.published_events.append(event)
        super().publish(events)
