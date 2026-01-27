from dataclasses import dataclass
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_status import OrderStatus

@dataclass
class Order:
      id: str
      tenant_id: str
      user_id: str
      products: dict[str, int]  # product_id to quantity
      amount: Money
      status: OrderStatus


      def __repr__(self) -> str:
            return f"Order(id={self.id}, tenant_id={self.tenant_id}, user_id={self.user_id}, products={self.products}, amount={self.amount}, status={self.status})"