from dataclasses import dataclass
import uuid

from app.domain.entities.order import Order
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.wallet_repository import WalletRepository


@dataclass
class PlaceOrder:
    order_repo: OrderRepository
    product_repo: ProductRepository
    wallet_repo: WalletRepository
    tenant_repo: TenantRepository
    event_bus: EventBus

    def execute(self, tenant_id: str, user_id: str, items: list[OrderItem]) -> Order:
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        total_amount = Money(0)
        product_entities = []
        for item in items:
            product = self.product_repo.get_by_id(tenant_id, item.product_id)

            if not product:
                raise DomainError(f"Product {item.product_id} does not exist.")

            product.reduce_stock(item.quantity)
            product_entities.append(product)
            total_amount = total_amount.add(item.total())

        wallet = self.wallet_repo.get_wallet(tenant_id, user_id)
        if wallet is None:
            raise DomainError("Wallet does not exist")

        order = Order(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            items=items,
            amount=total_amount,
        )
        wallet_entry = wallet.debit(total_amount, reference_id=order.id)
        order.mark_paid()

        for product in product_entities:
            self.product_repo.save(product)

        self.wallet_repo.append_entry(wallet_entry)
        self.order_repo.save(order)

        self.event_bus.publish([*wallet.events, *order.events])
        wallet.clear_events()
        order.clear_events()

        return order
