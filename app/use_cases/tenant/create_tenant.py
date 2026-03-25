from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.tenant import Tenant
from app.domain.events.tenant_created import TenantCreated
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.domain.exceptions import DomainError
from app.interfaces.event_bus import EventBus


@dataclass
class CreateTenant:
    tenant_repo: TenantRepository
    event_bus: EventBus

    def execute(self, name: str) -> Tenant:

        if not name or not name.strip():
            raise DomainError("Tenant name cannot be empty")
        if self.tenant_repo.get_by_name(name):
                  raise DomainError("Name already in use")

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name.strip()
        )

        self.tenant_repo.save(tenant)
        tenant.record_event(
            TenantCreated(
                tenant_id=tenant.id,
                name=tenant.name,
                occurred_at=datetime.now(),
            )
        )
        self.event_bus.publish(tenant.events)
        tenant.clear_events()
        return tenant
