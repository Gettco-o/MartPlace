from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_active_buyer


@dataclass
class RemoveFromCart:
    cart_repo: CartRepository
    user_repo: UserRepository

    async def execute(
        self,
        actor_user_id: str,
        user_id: str,
        tenant_id: str,
        product_id: str,
    ):
        await ensure_active_buyer(self.user_repo, actor_user_id, user_id)
        cart = await self.cart_repo.get_by_user(user_id)
        if cart is None:
            raise DomainError("Cart not found")

        existing_count = len(cart.items)
        cart.remove_item(product_id=product_id, tenant_id=tenant_id)
        if len(cart.items) == existing_count:
            raise DomainError("Item not found in cart")

        await self.cart_repo.save(cart)
        return cart
