from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class TenantActivated(DomainEvent):
    tenant_id: str
