from dataclasses import dataclass
from app.domain.events.base import DomainEvent


@dataclass
class OrderFailed(DomainEvent):
    order_id: str
    tenant_id: str
    user_id: str