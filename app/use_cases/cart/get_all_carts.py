from dataclasses import dataclass

from app.domain.entities.cart import Cart
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_platform_admin


@dataclass
class GetAllCarts:
    cart_repo: CartRepository
    user_repo: UserRepository

    async def execute(self, actor_user_id: str) -> list[Cart]:
        await ensure_platform_admin(self.user_repo, actor_user_id)
        return await self.cart_repo.list_all()
