from abc import ABC, abstractmethod
from app.domain.entities.cart import Cart

class CartRepository(ABC):
      @abstractmethod
      async def get_by_user(self, user_id: str) -> Cart | None:
            """Fetch the cart for a given user. Returns None if no cart exists."""
            pass
      
      @abstractmethod
      async def save(self, cart: Cart) -> None:
            """Persist the cart state."""
            pass
      
      @abstractmethod
      async def delete(self, cart_id: str) -> None:
            """Delete a cart by its ID."""
            pass

      @abstractmethod
      async def list_all(self) -> list[Cart]:
            """Return all carts."""
            pass
