from abc import ABC, abstractmethod
from app.domain.entities.tenant import Tenant

class TenantRepository(ABC):

      @abstractmethod
      async def save(self, tenant: Tenant) -> None:
            pass

      @abstractmethod
      async def get_by_id(self, tenant_id: str) -> Tenant | None:
            pass

      @abstractmethod
      async def get_by_name(self, tenant_name: str) -> Tenant | None:
            pass

      @abstractmethod
      async def list_all(self) -> list[Tenant]:
            pass
