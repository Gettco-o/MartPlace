from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class TenantUserRegistered(DomainEvent):
    user_id: str
    tenant_id: str
    email: str
    role: str
