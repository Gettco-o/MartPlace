from abc import ABC, abstractmethod
from app.domain.entities.tenant import Tenant

class TenantRepository(ABC):

      @abstractmethod
      def save(self, tenant: Tenant) -> None:
            pass

      @abstractmethod
      def get_by_id(self, tenant_id: str) -> Tenant | None:
            pass
      