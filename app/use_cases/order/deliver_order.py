from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager


@dataclass
class DeliverOrder:
    order_repo: OrderRepository
    tenant_repo: TenantRepository
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

        order.mark_delivered()
        await self.order_repo.save(order)
        self.event_bus.publish(order.events)
        order.clear_events()
        return order
