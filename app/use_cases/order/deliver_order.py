from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.tenant_wallet_repository import TenantWalletRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager
from app.domain.entities.tenant_wallet import TenantWallet
from app.domain.value_objects.user_role import UserRole


@dataclass
class DeliverOrder:
    order_repo: OrderRepository
    tenant_repo: TenantRepository
    tenant_wallet_repo: TenantWalletRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(self, actor_user_id: str, tenant_id: str, order_id: str):
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_tenant_manager(self.user_repo, actor_user_id, tenant_id)

        order = await self.order_repo.get_by_id(tenant_id, order_id)
        if not order:
            raise DomainError("Order not found")

        buyer = await self.user_repo.get_by_id(order.user_id)
        if not buyer:
            raise DomainError("Buyer not found")

        tenant_admin_emails = tuple(
            user.email
            for user in await self.user_repo.list_by_tenant(tenant_id)
            if user.role == UserRole.TENANT_ADMIN
        )

        order.mark_delivered(
            user_email=buyer.email,
            tenant_admin_emails=tenant_admin_emails,
        )
        wallet = await self.tenant_wallet_repo.get_wallet(tenant_id)
        if wallet is None:
            wallet = TenantWallet(tenant_id=tenant_id)

        reference_id = f"sale:{order.id}"
        if not await self.tenant_wallet_repo.has_reference(tenant_id, reference_id):
            entry = wallet.credit(order.amount, reference_id=reference_id)
            await self.tenant_wallet_repo.append_entry(entry)

        await self.order_repo.save(order)
        self.event_bus.publish(order.events)
        order.clear_events()
        return order
