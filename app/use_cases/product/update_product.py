from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.product import Product
from app.domain.events.product_updated import ProductUpdated
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.cart_repository import CartRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager


@dataclass
class UpdateProduct:
    cart_repo: CartRepository
    product_repo: ProductRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(
        self,
        actor_user_id: str,
        tenant_id: str,
        product_id: str,
        name: str | None = None,
        price: Money | None = None,
        stock: int | None = None,
    ) -> Product:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_tenant_manager(self.user_repo, actor_user_id, tenant_id)

        product = await self.product_repo.get_by_id(tenant_id, product_id)
        if not product:
            raise DomainError("Product not found")

        if name is None and price is None and stock is None:
            raise DomainError("At least one field must be provided for update")

        if name is not None:
            if not name.strip():
                raise DomainError("Product name cannot be empty")

            product_name = name.strip()
            if product_name != product.name and await self.product_repo.exists_by_name(
                tenant_id, product_name
            ):
                raise DomainError("Product name already in use")
            product.name = product_name

        price_changed = False
        if price is not None:
            if price.amount <= 0:
                raise DomainError("Price must be greater than zero")
            price_changed = price.amount != product.price.amount
            product.price = price

        if stock is not None:
            if stock < 0:
                raise DomainError("Stock cannot be negative")
            product.stock = stock

        await self.product_repo.save(product)
        if price_changed:
            for cart in await self.cart_repo.list_all():
                cart.refresh_item_price(
                    product_id=product.id,
                    tenant_id=tenant_id,
                    unit_price=product.price,
                )
                await self.cart_repo.save(cart)

        product.record_event(
            ProductUpdated(
                product_id=product.id,
                tenant_id=product.tenant_id,
                name=product.name,
                price_amount=product.price.amount,
                stock=product.stock,
                occurred_at=datetime.now(),
            )
        )
        self.event_bus.publish(product.events)
        product.clear_events()
        return product
