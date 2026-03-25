from dataclasses import dataclass, field

from app.domain.entities.order import Order
from app.domain.value_objects.order_item import OrderItem
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.domain.entities.idempotency import IdempotencyRecord
from app.use_cases.order.place_order import PlaceOrder

@dataclass
class CreateOrder:
    order_repo: OrderRepository
    product_repo: ProductRepository
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

    def execute(
        self,
        actor_user_id: str,
        tenant_id: str,
        user_id: str,
        items: list[OrderItem],
        idempotency_key: str,
    ) -> Order:
        operation = IdempotentOperation.CREATE_ORDER

        existing = self.idempotency_repo.get(idempotency_key, operation)
        if existing:
            return self.order_repo.get_by_id(tenant_id, existing.result_id)

        order = self.place_order.execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            user_id=user_id,
            items=items,
        )

        self.idempotency_repo.save(
            IdempotencyRecord(
                key=idempotency_key,
                operation=operation,
                result_id=order.id,
            )
        )

        return order
