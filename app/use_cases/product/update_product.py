from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.product import Product
from app.domain.events.product_updated import ProductUpdated
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class UpdateProduct:
    product_repo: ProductRepository
    tenant_repo: TenantRepository
    event_bus: EventBus

    def execute(
        self,
        tenant_id: str,
        product_id: str,
        name: str,
        price: Money,
        stock: int,
    ) -> Product:
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        product = self.product_repo.get_by_id(tenant_id, product_id)
        if not product:
            raise DomainError("Product not found")

        if not name or not name.strip():
            raise DomainError("Product name cannot be empty")

        if price.amount <= 0:
            raise DomainError("Price must be greater than zero")

        if stock < 0:
            raise DomainError("Stock cannot be negative")

        product_name = name.strip()
        if product_name != product.name and self.product_repo.exists_by_name(
            tenant_id, product_name
        ):
            raise DomainError("Product name already in use")

        product.name = product_name
        product.price = price
        product.stock = stock

        self.product_repo.save(product)
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
