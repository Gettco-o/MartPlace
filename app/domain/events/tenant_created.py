from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class TenantCreated(DomainEvent):
    tenant_id: str
    name: str
