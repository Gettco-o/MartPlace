from datetime import datetime
import json
import logging

from app.domain.events.buyer_registered import BuyerRegistered
from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_refunded import OrderRefunded
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.infrastructure.event_bus import SimpleEventBus
from app.infrastructure.event_handlers import register_email_handlers
from app.infrastructure.event_handlers.audit_logger import register_audit_log_handlers
from app.infrastructure.event_handlers.file_logger import register_event_file_handlers
from app.infrastructure.services.file_email_service import FileEmailService


def test_audit_log_handler_is_invoked_for_registered_event(caplog):
    event_bus = SimpleEventBus()
    register_audit_log_handlers(event_bus)

    event = OrderCreated(
        order_id="order-1",
        tenant_id="tenant-1",
        user_id="user-1",
        user_email="buyer@example.com",
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
        user_email="buyer@example.com",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["event_type"] == "OrderCreated"
    assert payload["payload"]["order_id"] == "order-2"


def test_order_created_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = OrderCreated(
        order_id="order-3",
        tenant_id="tenant-9",
        user_id="user-1",
        user_email="buyer@example.com",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["to"] == "buyer@example.com"
    assert payload["subject"] == "Order order-3 created successfully"
    assert "tenant-9" in payload["body"]


def test_tenant_order_created_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = OrderCreated(
        order_id="order-tenant-1",
        tenant_id="tenant-9",
        user_id="user-1",
        user_email="buyer@example.com",
        tenant_admin_emails=("admin1@tenant.com", "admin2@tenant.com"),
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3

    payloads = [json.loads(line) for line in lines]
    tenant_payloads = [payload for payload in payloads if payload["to"].endswith("@tenant.com")]
    assert len(tenant_payloads) == 2
    assert tenant_payloads[0]["subject"] == "New order order-tenant-1 received"


def test_buyer_registered_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = BuyerRegistered(
        user_id="user-1",
        email="buyer@example.com",
        name="Buyer",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[0])
    assert payload["to"] == "buyer@example.com"
    assert payload["subject"] == "Welcome to MartPlace"
    assert "Buyer" in payload["body"]


def test_tenant_user_registered_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = TenantUserRegistered(
        user_id="user-9",
        tenant_id="tenant-7",
        email="staff@example.com",
        role="tenant_staff",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[0])
    assert payload["to"] == "staff@example.com"
    assert payload["subject"] == "Your MartPlace tenant account is ready"
    assert "tenant-7" in payload["body"]


def test_order_status_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = OrderDelivered(
        order_id="order-4",
        tenant_id="tenant-2",
        user_id="user-1",
        user_email="buyer@example.com",
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[0])
    assert payload["to"] == "buyer@example.com"
    assert payload["subject"] == "Order order-4 has been delivered"
    assert "tenant-2" in payload["body"]


def test_tenant_order_cancelled_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = OrderCancelled(
        order_id="order-5",
        tenant_id="tenant-2",
        user_id="user-1",
        user_email="buyer@example.com",
        tenant_admin_emails=("admin@tenant.com",),
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]
    tenant_payload = next(payload for payload in payloads if payload["to"] == "admin@tenant.com")
    assert tenant_payload["subject"] == "Order order-5 was cancelled"


def test_tenant_order_refunded_handler_writes_email_to_file(tmp_path):
    event_bus = SimpleEventBus()
    email_log_path = tmp_path / "emails.log"
    email_service = FileEmailService(email_log_path)
    register_email_handlers(event_bus, email_service)

    event = OrderRefunded(
        order_id="order-6",
        tenant_id="tenant-4",
        user_id="user-1",
        user_email="buyer@example.com",
        tenant_admin_emails=("admin@tenant.com",),
        occurred_at=datetime.now(),
    )

    event_bus.publish([event])

    lines = email_log_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]
    tenant_payload = next(payload for payload in payloads if payload["to"] == "admin@tenant.com")
    assert tenant_payload["subject"] == "Order order-6 was refunded"
