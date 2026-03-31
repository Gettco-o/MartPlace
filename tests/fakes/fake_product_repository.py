from app.interfaces.repositories.product_repository import ProductRepository
from app.domain.entities.product import Product

class FakeProductRepository(ProductRepository):

    def __init__(self):
        self.products: dict[tuple[str,str], Product] = {}

    async def get_by_id(self, tenant_id: str, product_id: str) -> Product:
        return self.products.get((tenant_id, product_id))

    async def list_all(self, tenant_id: str | None = None) -> list[Product]:
        if tenant_id is None:
            return list(self.products.values())
        return [
            product
            for product in self.products.values()
            if product.tenant_id == tenant_id
        ]

    async def save(self, product: Product):
        key = (product.tenant_id, product.id)
        self.products[key] = product

    async def exists_by_name(self, tenant_id: str, name: str) -> bool:
        return any(
            product.tenant_id == tenant_id and product.name == name
            for product in self.products.values()
        )
        
