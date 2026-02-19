from dataclasses import dataclass
from datetime import datetime
from app.domain.events.base import DomainEvent


@dataclass
class OrderCreated(DomainEvent):
    order_id: str
    tenant_id: str
    user_id: str