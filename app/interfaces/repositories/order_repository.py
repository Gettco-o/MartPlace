from abc import ABC, abstractmethod
from app.domain.entities.order import Order

class OrderRepository(ABC):
      @abstractmethod
      async def save(self, order: Order) -> None:
            pass

      @abstractmethod
      async def get_by_id(self, tenant_id: str, order_id: str) -> Order | None:
            pass

      @abstractmethod
      async def list_all(self, tenant_id: str) -> list[Order]:
            pass
