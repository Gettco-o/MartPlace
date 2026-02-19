from dataclasses import dataclass
from app.domain.entities.idempotency import IdempotencyRecord
from app.domain.exceptions import DomainError
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.domain.value_objects.order_status import OrderStatus
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.wallet_repository import WalletRepository


@dataclass
class RefundOrder:
      order_repo: OrderRepository
      product_repo: ProductRepository
      wallet_repo: WalletRepository
      idempotency_repo: IdempotencyRepository

      def execute(self, tenant_id: str, order_id: str, idempotency_key: str):
            operation = IdempotentOperation.REFUND_ORDER

            existing = self.idempotency_repo.get(idempotency_key, operation)
            if existing:
                  return self.order_repo.get_by_id(tenant_id, order_id)
            
            order = self.order_repo.get_by_id(tenant_id, order_id)
            if not order:
                  raise DomainError("Order not found")
            
            if not order.can_refund():
                  raise DomainError("Order cannot be refunded")
                        
            # Restore stock
            for product_id, quantity in order.products.items():
                  product = self.product_repo.get_by_id(tenant_id, product_id)
                  product.increase_stock(quantity)
                  self.product_repo.save(product)

            # Credit wallet
            wallet = self.wallet_repo.get_wallet(tenant_id, order.user_id)
            wallet.credit(order.amount)
            self.wallet_repo.save(wallet)

            # Update order
            order.status = OrderStatus.REFUNDED
            self.order_repo.save(order)

            # Save idempotency record LAST
            self.idempotency_repo.save(
                  IdempotencyRecord(
                  key=idempotency_key,
                  operation=operation,
                  result_id=order.id,
                  )
            )

            return order
