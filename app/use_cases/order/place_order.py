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
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_active_buyer
from app.domain.value_objects.user_role import UserRole


@dataclass
class PlaceOrder:
    order_repo: OrderRepository
    product_repo: ProductRepository
    wallet_repo: WalletRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(
        self,
        actor_user_id: str,
        tenant_id: str,
        user_id: str,
        items: list[OrderItem],
    ) -> Order:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        buyer = await ensure_active_buyer(self.user_repo, actor_user_id, user_id)

        total_amount = Money(0)
        product_entities = []
        normalized_items = []
        for item in items:
            product = await self.product_repo.get_by_id(tenant_id, item.product_id)

            if not product:
                raise DomainError(f"Product {item.product_id} does not exist.")

            product.reduce_stock(item.quantity)
            product_entities.append(product)
            normalized_item = OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            normalized_items.append(normalized_item)
            total_amount = total_amount.add(normalized_item.total())

        wallet = await self.wallet_repo.get_wallet(user_id)
        if wallet is None:
            raise DomainError("Wallet does not exist")

        tenant_admin_emails = tuple(
            user.email
            for user in await self.user_repo.list_by_tenant(tenant_id)
            if user.role == UserRole.TENANT_ADMIN
        )

        order = Order(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            items=normalized_items,
            amount=total_amount,
        )
        wallet_entry = wallet.debit(total_amount, reference_id=order.id)
        order.mark_paid(
            user_email=buyer.email,
            tenant_admin_emails=tenant_admin_emails,
        )

        for product in product_entities:
            await self.product_repo.save(product)

        await self.wallet_repo.append_entry(wallet_entry)
        await self.order_repo.save(order)

        self.event_bus.publish([*wallet.events, *order.events])
        wallet.clear_events()
        order.clear_events()

        return order
