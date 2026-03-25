from dataclasses import dataclass
from collections import defaultdict
from app.domain.entities.idempotency import IdempotencyRecord
from app.domain.entities.order import Order
from app.domain.exceptions import DomainError
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
import uuid

from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.wallet_repository import WalletRepository

@dataclass
class CheckoutCart:
    cart_repo: CartRepository
    product_repo: ProductRepository
    order_repo: OrderRepository
    wallet_repo: WalletRepository
    idempotency_repo: IdempotencyRepository
    event_bus: EventBus

    def execute(self, user_id: str, idempotency_key: str) -> list[Order]:

        operation = IdempotentOperation.CHECKOUT_CART
        existing = self.idempotency_repo.get(idempotency_key, operation)
        if existing:
            return [
                self.order_repo.get_by_id(tenant_id, order_id)
                for tenant_id, order_id in existing.result_id
            ]

        cart = self.cart_repo.get_by_user(user_id)

        if not cart or cart.is_empty():
            raise DomainError("Cart is empty")

        # 2️⃣ Group cart items by tenant
        grouped = defaultdict(list)

        for item in cart.items:
            grouped[item.tenant_id].append(item)

        created_orders = []

        # 3️⃣ Process each tenant separately
        for tenant_id, items in grouped.items():

            order_items = []
            total = Money(0)

            for cart_item in items:
                product = self.product_repo.get_by_id(
                    tenant_id,
                    cart_item.product_id
                )

                if not product:
                    raise DomainError("Product not found")

                if product.stock < cart_item.quantity:
                    raise DomainError("Insufficient stock")

                # Reduce stock
                product.reduce_stock(cart_item.quantity)
                self.product_repo.save(product)

                order_item = OrderItem(
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price
                )

                order_items.append(order_item)
                total = total.add(order_item.total())

            # Debit wallet per tenant order
            wallet = self.wallet_repo.get_wallet(tenant_id, user_id)
            if not wallet:
                raise DomainError("Wallet not found")

            order = Order(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                items=order_items,
                amount=total,
            )
            wallet_entry = wallet.debit(total, reference_id=order.id)
            order.mark_paid()

            self.wallet_repo.append_entry(wallet_entry)
            self.order_repo.save(order)
            self.event_bus.publish([*wallet.events, *order.events])
            wallet.clear_events()
            order.clear_events()
            created_orders.append(order)

        # 4️⃣ Clear cart only after success
        cart.clear()
        self.cart_repo.save(cart)

        # 5️⃣ Store idempotent result
        self.idempotency_repo.save(
            IdempotencyRecord(
                key=idempotency_key,
                operation=operation,
                result_id=[(order.tenant_id, order.id) for order in created_orders],
            )
        )

        return created_orders
