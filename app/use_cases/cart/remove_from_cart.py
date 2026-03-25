from dataclasses import dataclass

from app.domain.exceptions import DomainError
from app.interfaces.repositories.cart_repository import CartRepository


@dataclass
class RemoveFromCart:
    cart_repo: CartRepository

    def execute(self, user_id: str, tenant_id: str, product_id: str):
        cart = self.cart_repo.get_by_user(user_id)
        if cart is None:
            raise DomainError("Cart not found")

        existing_count = len(cart.items)
        cart.remove_item(product_id=product_id, tenant_id=tenant_id)
        if len(cart.items) == existing_count:
            raise DomainError("Item not found in cart")

        self.cart_repo.save(cart)
        return cart
