from datetime import datetime
import json
import logging

from app.domain.events.order_created import OrderCreated
from app.infrastructure.event_bus import SimpleEventBus
from app.infrastructure.event_handlers.audit_logger import register_audit_log_handlers
from app.infrastructure.event_handlers.file_logger import register_event_file_handlers


def test_audit_log_handler_is_invoked_for_registered_event(caplog):
    event_bus = SimpleEventBus()
    register_audit_log_handlers(event_bus)

    event = OrderCreated(
        order_id="order-1",
        tenant_id="tenant-1",
        user_id="user-1",
        occurred_at=datetime.now(),
    )

    with caplog.at_level(logging.INFO, logger="martplace.audit"):
        event_bus.publish([event])

    assert "domain_event=OrderCreated" in caplog.text
    assert "order-1" in caplog.text


def test_file_log_handler_writes_published_event(tmp_path):
    event_bus = SimpleEventBus()
    log_path = tmp_path / "events.log"
    register_event_file_handlers(event_bus, log_path)

    event = OrderCreated(
        order_id="order-2",
        tenant_id="tenant-1",
        user_id="user-1",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["event_type"] == "OrderCreated"
    assert payload["payload"]["order_id"] == "order-2"
