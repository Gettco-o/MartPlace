from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.domain.entities.product import Product
from app.domain.value_objects.tenant_status import TenantStatus
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class GetAllProducts:
    product_repo: ProductRepository
    tenant_repo: TenantRepository

    async def execute(self, tenant_id: str | None = None) -> list[Product]:
        if tenant_id is not None:
            tenant = await self.tenant_repo.get_by_id(tenant_id)
            if tenant is None:
                raise DomainError("Tenant not found")

            tenant.ensure_active()
            return await self.product_repo.list_all(tenant_id)

        active_tenant_ids = {
            tenant.id
            for tenant in await self.tenant_repo.list_all()
            if tenant.status == TenantStatus.ACTIVE
        }
        return [
            product
            for product in await self.product_repo.list_all()
            if product.tenant_id in active_tenant_ids
        ]
