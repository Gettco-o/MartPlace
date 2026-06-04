import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
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


def _serialize_event(event: Any) -> dict[str, Any]:
    if is_dataclass(event):
        payload = asdict(event)
    else:
        payload = {"repr": repr(event)}

    for key, value in list(payload.items()):
        if isinstance(value, datetime):
            payload[key] = value.isoformat()

    return {
        "event_type": type(event).__name__,
        "payload": payload,
        "logged_at": datetime.now().isoformat(),
    }


def _append_event(log_path: Path, event: Any) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_serialize_event(event), default=str) + "\n")


def register_event_file_handlers(event_bus: EventBus, log_path: str | Path) -> None:
    path = Path(log_path)
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
        event_bus.register(event_type, lambda event, path=path: _append_event(path, event))
