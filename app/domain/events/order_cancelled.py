from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class OrderCancelled(DomainEvent):
    order_id: str
    tenant_id: str
    user_id: str
    user_email: str
    tenant_admin_emails: tuple[str, ...] = ()
