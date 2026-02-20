from dataclasses import dataclass
from app.domain.value_objects.money import Money
from app.domain.exceptions import DomainError

@dataclass
class Product:
      id: str
      tenant_id: str
      name: str
      price: Money
      stock: int

      def reduce_stock(self, quantity: int):
            if quantity < 0:
                  raise DomainError("Quantity must be positive")
            if self.stock < quantity:
                  raise DomainError("Insufficient stock")
            
            self.stock -= quantity

      def increase_stock(self, quantity: int):
            if quantity <= 0:
                  raise DomainError("Quantity must be greater than zero")

            self.stock += quantity