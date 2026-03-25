from dataclasses import dataclass
import uuid

from app.domain.entities.cart import Cart
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_active_buyer


@dataclass
class AddToCart:
    cart_repo: CartRepository
    product_repo: ProductRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository

    def execute(
        self,
        actor_user_id: str,
        user_id: str,
        tenant_id: str,
        product_id: str,
        quantity: int,
    ) -> Cart:
        if quantity <= 0:
            raise DomainError("Quantity must be greater than zero")

        ensure_active_buyer(self.user_repo, actor_user_id, user_id)

        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        product = self.product_repo.get_by_id(tenant_id, product_id)
        if not product:
            raise DomainError("Product not found")

        cart = self.cart_repo.get_by_user(user_id)
        if cart is None:
            cart = Cart(
                id=str(uuid.uuid4()),
                user_id=user_id,
            )

        cart.add_item(
            CartItem(
                product_id=product.id,
                tenant_id=tenant_id,
                quantity=quantity,
                unit_price=product.price,
            )
        )
        self.cart_repo.save(cart)

        return cart
