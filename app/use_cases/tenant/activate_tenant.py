from dataclasses import dataclass
from app.domain.entities.tenant import Tenant
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.domain.exceptions import DomainError

@dataclass
class ActivateTenant:
    tenant_repo: TenantRepository

    def execute(self, tenant_id: str) -> Tenant:
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.activate()
        self.tenant_repo.save(tenant)

        return tenant