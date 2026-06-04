from app.domain.entities.tenant import Tenant
from app.interfaces.repositories.tenant_repository import TenantRepository

class FakeTenantRepository(TenantRepository):
      def __init__(self):
            self.tenants: dict[str, Tenant] = {}

      async def save(self, tenant: Tenant) -> None:
            self.tenants[tenant.id] = tenant

      async def get_by_id(self, tenant_id: str) -> Tenant | None:
            return self.tenants.get(tenant_id)
      
      async def get_by_name(self, tenant_name: str) -> Tenant | None:
            for tenant in self.tenants.values():
                  if tenant.name == tenant_name:
                        return tenant
            return None

      async def list_all(self) -> list[Tenant]:
            return list(self.tenants.values())
