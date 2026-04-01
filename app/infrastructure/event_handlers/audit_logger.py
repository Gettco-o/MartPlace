import logging
from dataclasses import asdict, is_dataclass
from typing import Any

from app.domain.events.buyer_registered import BuyerRegistered
from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_failed import OrderFailed
from app.domain.events.order_fulfilled import OrderFulfilled
from app.domain.events.order_processing_started import OrderProcessingStarted
from app.domain.events.order_refunded import OrderRefunded
from app.domain.events.product_created import ProductCreated
from app.domain.events.product_updated import ProductUpdated
from app.domain.events.tenant_activated import TenantActivated
from app.domain.events.tenant_created import TenantCreated
from app.domain.events.tenant_suspended import TenantSuspended
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.domain.events.wallet_credited import WalletCredited
from app.domain.events.wallet_debited import WalletDebited
from app.interfaces.event_bus import EventBus


logger = logging.getLogger("martplace.audit")


def _event_payload(event: Any) -> dict[str, Any]:
    if is_dataclass(event):
        return asdict(event)
    return {"repr": repr(event)}


def log_domain_event(event: Any) -> None:
    logger.info(
        "domain_event=%s payload=%s",
        type(event).__name__,
        _event_payload(event),
    )


def register_audit_log_handlers(event_bus: EventBus) -> None:
    event_types = [
        BuyerRegistered,
        OrderCancelled,
        OrderCreated,
        OrderDelivered,
        OrderFailed,
        OrderFulfilled,
        OrderProcessingStarted,
        OrderRefunded,
        ProductCreated,
        ProductUpdated,
        TenantActivated,
        TenantCreated,
        TenantSuspended,
        TenantUserRegistered,
        WalletCredited,
        WalletDebited,
    ]

    for event_type in event_types:
        event_bus.register(event_type, log_domain_event)
