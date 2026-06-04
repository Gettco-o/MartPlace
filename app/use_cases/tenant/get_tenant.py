from dataclasses import dataclass

from app.domain.entities.tenant import Tenant
from app.domain.exceptions import DomainError
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class GetTenant:
    tenant_repo: TenantRepository

    async def execute(self, tenant_id: str) -> Tenant:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if tenant is None:
            raise DomainError("Tenant not found")
        return tenant
