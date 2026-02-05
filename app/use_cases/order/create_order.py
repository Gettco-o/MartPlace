from dataclasses import dataclass
from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_status import OrderStatus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.exceptions import DomainError
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.domain.entities.idempotency import IdempotencyRecord
import uuid

@dataclass
class CreateOrder:
      order_repo: OrderRepository
      product_repo: ProductRepository
      wallet_repo: WalletRepository
      idempotency_repo: IdempotencyRepository

      def execute(self, tenant_id: str, user_id: str, products: dict[str, int], idempotency_key: str) -> Order:

            operation = IdempotentOperation.CREATE_ORDER

            existing = self.idempotency_repo.get(idempotency_key, operation)
            if existing:
                  return self.order_repo.get_by_id(tenant_id, existing.result_id)

            total_amount = Money(0)
            product_entities = []
            for product_id, quantity in products.items():
                  product = self.product_repo.get_by_id(tenant_id, product_id)

                  if not product:
                        raise DomainError(f"Product {product_id} does not exist.")
                  
                  product.reduce_stock(quantity)
                  product_entities.append(product)
                  
                  total_amount = total_amount.add(product.price.multiply(quantity))
            
            wallet = self.wallet_repo.get_wallet(tenant_id, user_id)
            if wallet is None:
                  raise DomainError("Wallet does not exist")

            wallet.debit(total_amount)

            order = Order(
                  id = str(uuid.uuid4()),
                  tenant_id = tenant_id,
                  user_id = user_id,
                  products = products,
                  amount = total_amount,
                  status = OrderStatus.PAID,
            )

            for product in product_entities:
                  self.product_repo.save(product)

            self.wallet_repo.save(wallet)
            self.order_repo.save(order)

            self.idempotency_repo.save(
                  IdempotencyRecord(
                        key=idempotency_key,
                        operation=operation,
                        result_id=order.id
                  )
            )

            return order