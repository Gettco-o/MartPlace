# tests/fakes/fake_product_repository.py
from app.interfaces.repositories.product_repository import ProductRepository

class FakeProductRepository(ProductRepository):

    def __init__(self):
        self.products = []

    def get_product_by_id(self, tenant__id, product_id: str):
        for product in self.products:
            if product.tenant_id==tenant__id and product.id==product_id:
                return product
        return None

    def add(self, product):
        self.products.append(product)
