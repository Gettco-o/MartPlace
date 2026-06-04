from dataclasses import dataclass

from app.domain.entities.tenant_wallet import TenantWallet
from app.domain.exceptions import DomainError
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.tenant_wallet_repository import TenantWalletRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager


@dataclass
class GetTenantWallet:
    tenant_wallet_repository: TenantWalletRepository
    tenant_repository: TenantRepository
    user_repository: UserRepository

    async def execute(self, actor_user_id: str, tenant_id: str) -> TenantWallet:
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if tenant is None:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_tenant_manager(self.user_repository, actor_user_id, tenant_id)

        wallet = await self.tenant_wallet_repository.get_wallet(tenant_id)
        if wallet is None:
            return TenantWallet(tenant_id=tenant_id)

        return wallet
