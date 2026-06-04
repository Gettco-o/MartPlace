from abc import ABC, abstractmethod
from app.domain.entities.product import Product

class ProductRepository(ABC):
      @abstractmethod
      async def get_by_id(self, tenant_id: str, product_id: str) -> Product | None:
            pass

      @abstractmethod
      async def list_all(self, tenant_id: str | None = None) -> list[Product]:
            pass

      @abstractmethod
      async def save(self, product):
            pass

      @abstractmethod
      async def exists_by_name(self, tenant_id: str, name: str) -> bool: 
            pass
