from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_active_buyer


@dataclass
class CancelOrder:
    order_repo: OrderRepository
    product_repo: ProductRepository
    wallet_repo: WalletRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(self, actor_user_id: str, tenant_id: str, order_id: str):
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        order = await self.order_repo.get_by_id(tenant_id, order_id)
        if not order:
            raise DomainError("Order not found")

        await ensure_active_buyer(self.user_repo, actor_user_id, order.user_id)

        for item in order.items:
            product = await self.product_repo.get_by_id(tenant_id, item.product_id)
            product.increase_stock(item.quantity)
            await self.product_repo.save(product)

        wallet = await self.wallet_repo.get_wallet(tenant_id, order.user_id)
        if wallet is None:
            raise DomainError("Wallet does not exist")

        wallet_entry = wallet.credit(order.amount, reference_id=f"cancel:{order.id}")
        order.mark_cancelled()

        await self.wallet_repo.append_entry(wallet_entry)
        await self.order_repo.save(order)

        self.event_bus.publish([*wallet.events, *order.events])
        wallet.clear_events()
        order.clear_events()

        return order
