from dataclasses import dataclass, field
from datetime import datetime
from app.domain.entities.entity_with_events import EntityWithEvents
from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_failed import OrderFailed
from app.domain.events.order_fulfilled import OrderFulfilled
from app.domain.events.order_processing_started import OrderProcessingStarted
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
            return self.status in (
                  OrderStatus.PAID,
                  OrderStatus.PROCESSING,
                  OrderStatus.FULFILLED,
                  OrderStatus.DELIVERED,
            )

      def can_cancel(self) -> bool:
            return self.status == OrderStatus.PAID

      
      def mark_paid(self, user_email: str, tenant_admin_emails: tuple[str, ...] = ()):
            if self.status != OrderStatus.CREATED:
                  raise DomainError("Only ceated orders can be marked as PAID")
            self.status = OrderStatus.PAID
            self.record_event(
                  OrderCreated(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        tenant_admin_emails=tenant_admin_emails,
                        occurred_at=datetime.now(),
                  )
            )

      def start_processing(self, user_email: str):
            if self.status != OrderStatus.PAID:
                  raise DomainError("Only paid orders can be moved to PROCESSING")
            self.status = OrderStatus.PROCESSING
            self.record_event(
                  OrderProcessingStarted(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_fulfilled(self, user_email: str):
            if self.status != OrderStatus.PROCESSING:
                  raise DomainError("Only processing orders can be marked as FULFILLED")
            self.status = OrderStatus.FULFILLED
            self.record_event(
                  OrderFulfilled(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_delivered(self, user_email: str, tenant_admin_emails: tuple[str, ...] = ()):
            if self.status != OrderStatus.FULFILLED:
                  raise DomainError("Only fulfilled orders can be marked as DELIVERED")
            self.status = OrderStatus.DELIVERED
            self.record_event(
                  OrderDelivered(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        tenant_admin_emails=tenant_admin_emails,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_cancelled(self, user_email: str, tenant_admin_emails: tuple[str, ...] = ()):
            if not self.can_cancel():
                  raise DomainError("Only paid orders can be cancelled")
            self.status = OrderStatus.CANCELLED
            self.record_event(
                  OrderCancelled(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        tenant_admin_emails=tenant_admin_emails,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_refunded(self, user_email: str, tenant_admin_emails: tuple[str, ...] = ()):
            if not self.can_refund():
                  raise DomainError("Only paid orders can be refunded")
            self.status = OrderStatus.REFUNDED
            self.record_event(
                  OrderRefunded(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        tenant_admin_emails=tenant_admin_emails,
                        occurred_at=datetime.now(),
                  )
            )

      def mark_failed(self, user_email: str):
            if self.status != OrderStatus.CREATED:
                  raise DomainError("Only created orders can be marked as FAILED")
            self.status = OrderStatus.FAILED
            self.record_event(
                  OrderFailed(
                        order_id=self.id,
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        user_email=user_email,
                        occurred_at=datetime.now(),
                  )
            )
