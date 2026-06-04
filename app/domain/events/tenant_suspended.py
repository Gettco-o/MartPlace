from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class TenantSuspended(DomainEvent):
    tenant_id: str
