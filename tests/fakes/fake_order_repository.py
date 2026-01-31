# tests/fakes/fake_order_repository.py
from app.interfaces.repositories.order_repository import OrderRepository

class FakeOrderRepository(OrderRepository):

    def __init__(self):
        self.orders = []

    def save(self, order):
        self.orders.append(order)

    def get_order_by_id(self, tenant_id: str, order_id: str):
        for order in self.orders:
            if order.tenant_id == tenant_id and order.id == order_id:
                return order
        return None