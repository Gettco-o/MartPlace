from abc import ABC, abstractmethod
from app.domain.entities.order import Order

class OrderRepository(ABC):
      @abstractmethod
      def save(self, order: Order) -> None:
            pass

      @abstractmethod
      def get_order_by_id(self, tenant_id: str, order_id: str) -> Order | None:
            pass