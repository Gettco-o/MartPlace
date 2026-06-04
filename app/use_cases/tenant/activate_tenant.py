from dataclasses import dataclass
from app.domain.entities.tenant import Tenant
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_platform_admin
from app.domain.exceptions import DomainError

@dataclass
class ActivateTenant:
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(self, actor_user_id: str, tenant_id: str) -> Tenant:
        await ensure_platform_admin(self.user_repo, actor_user_id)
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.activate()
        await self.tenant_repo.save(tenant)
        self.event_bus.publish(tenant.events)
        tenant.clear_events()

        return tenant
