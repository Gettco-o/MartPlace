from dataclasses import dataclass
import uuid

from app.domain.entities.tenant import Tenant
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.domain.exceptions import DomainError


@dataclass
class CreateTenant:
    tenant_repo: TenantRepository

    def execute(self, name: str) -> Tenant:

        if not name or not name.strip():
            raise DomainError("Tenant name cannot be empty")

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name.strip(),
        )

        self.tenant_repo.save(tenant)
        return tenant