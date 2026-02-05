from abc import ABC, abstractmethod
from app.domain.entities.product import Product

class ProductRepository(ABC):
      @abstractmethod
      def get_by_id(self, tenant_id: str, product_id: str) -> Product | None:
            pass

      @abstractmethod
      def save(self, product):
            pass