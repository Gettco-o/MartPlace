from app.interfaces.repositories.product_repository import ProductRepository
from app.domain.entities.product import Product

class FakeProductRepository(ProductRepository):

    def __init__(self):
        self.products: dict[tuple[str,str], Product] = {}

    def get_by_id(self, tenant_id: str, product_id: str) -> Product:
        return self.products.get((tenant_id, product_id))

    def save(self, product: Product):
        key = (product.tenant_id, product.id)
        self.products[key] = product

    def exists_by_name(self, tenant_id: str, name: str) -> bool:
        return any(
            product.tenant_id == tenant_id and product.name == name
            for product in self.products.values()
        )
        
