from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.product import Product
from app.domain.events.product_created import ProductCreated
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager


@dataclass
class CreateProduct:
    product_repo: ProductRepository
    tenant_repo: TenantRepository
    user_repo: UserRepository
    event_bus: EventBus

    def execute(
        self,
        actor_user_id: str,
        tenant_id: str,
        name: str,
        price: Money,
        stock: int,
    ) -> Product:
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        ensure_tenant_manager(self.user_repo, actor_user_id, tenant_id)

        if not name or not name.strip():
            raise DomainError("Product name cannot be empty")

        if price.amount <= 0:
            raise DomainError("Price must be greater than zero")

        if stock < 0:
            raise DomainError("Stock cannot be negative")

        product_name = name.strip()
        if self.product_repo.exists_by_name(tenant_id, product_name):
            raise DomainError("Product name already in use")

        product = Product(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=product_name,
            price=price,
            stock=stock,
        )

        self.product_repo.save(product)
        product.record_event(
            ProductCreated(
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
