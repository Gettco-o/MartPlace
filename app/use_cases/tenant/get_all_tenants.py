from dataclasses import dataclass

from app.domain.entities.tenant import Tenant
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_platform_admin


@dataclass
class GetAllTenants:
    tenant_repo: TenantRepository
    user_repo: UserRepository

    async def execute(self, actor_user_id: str) -> list[Tenant]:
        await ensure_platform_admin(self.user_repo, actor_user_id)
        return await self.tenant_repo.list_all()
