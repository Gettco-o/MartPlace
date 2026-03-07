from app.interfaces.repositories.cart_repository import CartRepository
from app.domain.entities.cart import Cart


class FakeCartRepository(CartRepository):

    def __init__(self):
        self.carts: dict[str, Cart] = {}

    def get_by_user(self, user_id: str) -> Cart | None:
        return self.carts.get(user_id)

    def save(self, cart: Cart) -> None:
        self.carts[cart.user_id] = cart

    def delete(self, user_id: str) -> None:
        if user_id in self.carts:
            del self.carts[user_id]