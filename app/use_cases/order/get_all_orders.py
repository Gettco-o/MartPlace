from dataclasses import dataclass

from app.domain.entities.order import Order
from app.domain.exceptions import DomainError
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager


@dataclass
class GetAllOrders:
    order_repo: OrderRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository

    async def execute(self, actor_user_id: str, tenant_id: str) -> list[Order]:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if tenant is None:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_tenant_manager(self.user_repo, actor_user_id, tenant_id)
        return await self.order_repo.list_all(tenant_id)
