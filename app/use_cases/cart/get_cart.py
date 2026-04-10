from dataclasses import dataclass

from app.domain.entities.cart import Cart
from app.domain.exceptions import DomainError
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_active_buyer


@dataclass
class GetCart:
    cart_repo: CartRepository
    user_repo: UserRepository

    async def execute(self, actor_user_id: str, user_id: str) -> Cart:
        await ensure_active_buyer(self.user_repo, actor_user_id, user_id)

        cart = await self.cart_repo.get_by_user(user_id)
        if cart is None:
            raise DomainError("Cart not found")

        return cart
