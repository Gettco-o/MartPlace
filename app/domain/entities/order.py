from dataclasses import dataclass
from datetime import datetime
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_refunded import OrderRefunded
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
      created_at: datetime = datetime.now()


      def __repr__(self) -> str:
            return f"Order(id={self.id}, tenant_id={self.tenant_id}, user_id={self.user_id}, products={self.products}, amount={self.amount}, status={self.status})"
      
      def can_refund(self) -> bool:
            return self.status == OrderStatus.PAID
      
      def __post_init__(self):
            self._events = []

      @property
      def events(self):
            return self._events
      
      def mark_paid(self):
            self.status = OrderStatus.PAID
            self._events.append(
            OrderCreated(
                  order_id=self.id,
                  tenant_id=self.tenant_id,
                  user_id=self.user_id,
                  occurred_at=datetime.now(),
                  )
            )

      def mark_refunded(self):
            self.status = OrderStatus.REFUNDED
            self._events.append(
            OrderRefunded(
                  order_id=self.id,
                  tenant_id=self.tenant_id,
                  user_id=self.user_id,
                  occurred_at=datetime.now(),
                  )
            )

      def clear_events(self):
            self._events.clear()