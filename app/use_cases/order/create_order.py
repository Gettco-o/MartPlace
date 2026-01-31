from dataclasses import dataclass
from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_status import OrderStatus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
import uuid

@dataclass
class CreateOrder:
      order_repo: OrderRepository
      product_repo: ProductRepository
      wallet_repo: WalletRepository

      def execute(self, tenant_id: str, user_id: str, products: dict[str, int]) -> Order:
            total_amount = Money(0)
            for product_id, quantity in products.items():
                  product = self.product_repo.get_product_by_id(tenant_id, product_id)
                  if not product or product.stock < quantity:
                        raise ValueError(f"Product {product_id} is out of stock or does not exist.")
                  total_amount = total_amount.add(product.price.multiply(quantity))

            wallet = self.wallet_repo.get_wallet(tenant_id, user_id)
            if wallet.balance < total_amount:
                  raise ValueError("Insufficient funds in wallet.")
            wallet.debit(total_amount)

            order = Order(
                  id = str(uuid.uuid4()),
                  tenant_id = tenant_id,
                  user_id = user_id,
                  products = products,
                  amount = total_amount,
                  status = OrderStatus.CREATED,
            )

            self.wallet_repo.save(wallet)
            self.order_repo.save(order)

            return order