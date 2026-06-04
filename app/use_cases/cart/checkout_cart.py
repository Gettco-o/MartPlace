from dataclasses import dataclass, field
from collections import defaultdict

from app.domain.entities.idempotency import IdempotencyRecord
from app.domain.entities.order import Order
from app.domain.exceptions import DomainError
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.domain.value_objects.order_item import OrderItem

from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.order.place_order import PlaceOrder

@dataclass
class CheckoutCart:
    cart_repo: CartRepository
    product_repo: ProductRepository
    order_repo: OrderRepository
    wallet_repo: WalletRepository
    idempotency_repo: IdempotencyRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus
    place_order: PlaceOrder = field(init=False)

    def __post_init__(self) -> None:
        self.place_order = PlaceOrder(
            order_repo=self.order_repo,
            product_repo=self.product_repo,
            wallet_repo=self.wallet_repo,
            tenant_repo=self.tenant_repo,
            user_repo=self.user_repo,
            event_bus=self.event_bus,
        )

    async def execute(self, actor_user_id: str, user_id: str, idempotency_key: str) -> list[Order]:

        operation = IdempotentOperation.CHECKOUT_CART
        existing = await self.idempotency_repo.get(idempotency_key, operation)
        if existing:
            return [
                await self.order_repo.get_by_id(tenant_id, order_id)
                for tenant_id, order_id in existing.result_id
            ]

        cart = await self.cart_repo.get_by_user(user_id)

        if not cart or cart.is_empty():
            raise DomainError("Cart is empty")

        cart.ensure_active()

        grouped = defaultdict(list)

        for item in cart.items:
            grouped[item.tenant_id].append(item)

        created_orders = []

        for tenant_id, items in grouped.items():
            order_items = []

            for cart_item in items:
                order_items.append(
                    OrderItem(
                        product_id=cart_item.product_id,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price,
                    )
                )

            order = await self.place_order.execute(
                actor_user_id=actor_user_id,
                tenant_id=tenant_id,
                user_id=user_id,
                items=order_items,
            )
            created_orders.append(order)

        cart.complete()
        await self.cart_repo.save(cart)

        await self.idempotency_repo.save(
            IdempotencyRecord(
                key=idempotency_key,
                operation=operation,
                result_id=[(order.tenant_id, order.id) for order in created_orders],
            )
        )

        return created_orders
