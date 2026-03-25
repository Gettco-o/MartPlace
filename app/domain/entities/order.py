from dataclasses import dataclass, field
from datetime import datetime
from app.domain.entities.entity_with_events import EntityWithEvents
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_failed import OrderFailed
from app.domain.events.order_refunded import OrderRefunded
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.domain.value_objects.order_status import OrderStatus


@dataclass
class Order(EntityWithEvents):
      id: str
      tenant_id: str
      user_id: str
      items: list[OrderItem]
      amount: Money
      status: OrderStatus = OrderStatus.CREATED
      created_at: datetime = field(default_factory=datetime.now)
      
      def __repr__(self) -> str:
            return f"Order(id={self.id}, tenant_id={self.tenant_id}, user_id={self.user_id}, items={self.items}, amount={self.amount}, status={self.status})"
      
      def can_refund(self) -> bool:
            return self.status == OrderStatus.PAID

      
      def mark_paid(self):
            if self.status != OrderStatus.CREATED:
                  raise DomainError("Only ceated orders can be marked as PAID")
            self.status = OrderStatus.PAID
            self.record_event(
                  OrderCreated(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_refunded(self):
            if not self.can_refund():
                  raise DomainError("Only paid orders can be refunded")
            self.status = OrderStatus.REFUNDED
            self.record_event(
                  OrderRefunded(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_failed(self):
            if self.status != OrderStatus.CREATED:
                  raise DomainError("Only created orders can be marked as FAILED")
            self.status = OrderStatus.FAILED
            self.record_event(
                  OrderFailed(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        occurred_at=datetime.now(),
                  )
            )
