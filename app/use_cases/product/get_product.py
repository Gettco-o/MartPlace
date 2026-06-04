from dataclasses import dataclass

from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.interfaces.repositories.product_repository import ProductRepository


@dataclass
class GetProduct:
    product_repo: ProductRepository

    async def execute(self, tenant_id: str, product_id: str) -> Product:
        product = await self.product_repo.get_by_id(tenant_id, product_id)
        if product is None:
            raise DomainError("Product not found")
        return product
