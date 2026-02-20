from dataclasses import dataclass
from app.domain.value_objects.tenant_status import TenantStatus

@dataclass
class Tenant:
      id: str
      name: str
      status: TenantStatus = TenantStatus.ACTIVE

      def suspend(self):
            if self.status == TenantStatus.SUSPENDED:
                  raise ValueError("Tenant is already suspended")
            self.status = TenantStatus.SUSPENDED

      def activate(self):
            if self.status == TenantStatus.ACTIVE:
                  raise ValueError("Tenant is already active")
            self.status = TenantStatus.ACTIVE

      def ensure_active(self):
            if self.status != TenantStatus.ACTIVE:
                  raise ValueError("Tenant is not active")