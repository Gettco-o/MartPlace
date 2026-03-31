from dataclasses import dataclass

from app.domain.entities.tenant import Tenant
from app.domain.value_objects.tenant_status import TenantStatus
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class GetActiveTenants:
    tenant_repo: TenantRepository

    async def execute(self) -> list[Tenant]:
        return [
            tenant
            for tenant in await self.tenant_repo.list_all()
            if tenant.status == TenantStatus.ACTIVE
        ]
