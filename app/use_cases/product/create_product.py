from dataclasses import dataclass
import uuid

from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.tenant_repository import TenantRepository


@dataclass
class CreateProduct:
    product_repo: ProductRepository
    tenant_repo: TenantRepository

    def execute(self, tenant_id: str, name: str, price: Money, stock: int) -> Product:
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

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
        return product
