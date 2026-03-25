from dataclasses import dataclass
import uuid

from app.domain.entities.cart import Cart
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class AddToCart:
    cart_repo: CartRepository
    product_repo: ProductRepository
    tenant_repo: TenantRepository

    def execute(self, user_id: str, tenant_id: str, product_id: str, quantity: int) -> Cart:
        if quantity <= 0:
            raise DomainError("Quantity must be greater than zero")

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
