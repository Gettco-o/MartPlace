from dataclasses import dataclass
from app.domain.entities.idempotency import IdempotencyRecord
from app.domain.exceptions import DomainError
from app.domain.value_objects.idempotent_operation import IdempotentOperation
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.tenant_wallet_repository import TenantWalletRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_active_buyer
from app.domain.entities.tenant_wallet import TenantWallet
from app.domain.value_objects.order_status import OrderStatus
from app.domain.value_objects.user_role import UserRole


@dataclass
class RefundOrder:
    order_repo: OrderRepository
    product_repo: ProductRepository
    wallet_repo: WalletRepository
    tenant_wallet_repo: TenantWalletRepository
    idempotency_repo: IdempotencyRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(self, actor_user_id: str, tenant_id: str, order_id: str, idempotency_key: str):
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        operation = IdempotentOperation.REFUND_ORDER

        existing = await self.idempotency_repo.get(idempotency_key, operation)
        if existing:
            return await self.order_repo.get_by_id(tenant_id, order_id)

        order = await self.order_repo.get_by_id(tenant_id, order_id)
        if not order:
            raise DomainError("Order not found")

        should_reverse_tenant_wallet = order.status == OrderStatus.DELIVERED
        await ensure_active_buyer(self.user_repo, actor_user_id, order.user_id)

        for item in order.items:
            product = await self.product_repo.get_by_id(tenant_id, item.product_id)
            product.increase_stock(item.quantity)
            await self.product_repo.save(product)

        wallet = await self.wallet_repo.get_wallet(order.user_id)
        if wallet is None:
            raise DomainError("Wallet does not exist")

        wallet_entry = wallet.credit(order.amount, reference_id=f"refund:{order.id}")
        if should_reverse_tenant_wallet:
            tenant_wallet = await self.tenant_wallet_repo.get_wallet(tenant_id)
            if tenant_wallet is None:
                tenant_wallet = TenantWallet(tenant_id=tenant_id)

            reversal_reference = f"refund-reversal:{order.id}"
            if not await self.tenant_wallet_repo.has_reference(tenant_id, reversal_reference):
                tenant_wallet_entry = tenant_wallet.debit(
                    order.amount,
                    reference_id=reversal_reference,
                )
                await self.tenant_wallet_repo.append_entry(tenant_wallet_entry)

        buyer = await self.user_repo.get_by_id(order.user_id)
        if not buyer:
            raise DomainError("Buyer not found")

        tenant_admin_emails = tuple(
            user.email
            for user in await self.user_repo.list_by_tenant(tenant_id)
            if user.role == UserRole.TENANT_ADMIN
        )

        order.mark_refunded(
            user_email=buyer.email,
            tenant_admin_emails=tenant_admin_emails,
        )

        await self.wallet_repo.append_entry(wallet_entry)
        await self.order_repo.save(order)

        await self.idempotency_repo.save(
            IdempotencyRecord(
                key=idempotency_key,
                operation=operation,
                result_id=order.id,
            )
        )

        self.event_bus.publish([*wallet.events, *order.events])
        wallet.clear_events()
        order.clear_events()

        return order
