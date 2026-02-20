from app.domain.entities.tenant import Tenant
from app.interfaces.repositories.tenant_repository import TenantRepository

class FakeTenantRepository(TenantRepository):
      def __init__(self):
            self.tenants: dict[str, Tenant] = {}

      def save(self, tenant: Tenant) -> None:
            self.tenants[tenant.id] = tenant

      def get_by_id(self, tenant_id: str) -> Tenant | None:
            return self.tenants.get(tenant_id)