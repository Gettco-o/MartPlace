from dataclasses import dataclass

from app.domain.entities.wallet import Wallet
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_platform_admin


@dataclass
class GetAllWallets:
    wallet_repository: WalletRepository
    user_repository: UserRepository

    async def execute(self, actor_user_id: str) -> list[Wallet]:
        await ensure_platform_admin(self.user_repository, actor_user_id)
        return await self.wallet_repository.list_all()
