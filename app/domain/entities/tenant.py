from dataclasses import dataclass
from datetime import datetime
from app.domain.entities.entity_with_events import EntityWithEvents
from app.domain.events.tenant_activated import TenantActivated
from app.domain.events.tenant_suspended import TenantSuspended
from app.domain.exceptions import DomainError
from app.domain.value_objects.tenant_status import TenantStatus

@dataclass
class Tenant(EntityWithEvents):
      id: str
      name: str
      status: TenantStatus = TenantStatus.ACTIVE

      def suspend(self):
            if self.status == TenantStatus.SUSPENDED:
                  raise DomainError("Tenant is already suspended")
            self.status = TenantStatus.SUSPENDED
            self.record_event(
                  TenantSuspended(
                        tenant_id=self.id,
                        occurred_at=datetime.now(),
                  )
            )

      def activate(self):
            if self.status == TenantStatus.ACTIVE:
                  raise DomainError("Tenant is already active")
            self.status = TenantStatus.ACTIVE
            self.record_event(
                  TenantActivated(
                        tenant_id=self.id,
                        occurred_at=datetime.now(),
                  )
            )

      def ensure_active(self):
            if self.status != TenantStatus.ACTIVE:
                  raise DomainError("Tenant is not active")
