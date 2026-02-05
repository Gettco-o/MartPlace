# tests/fakes/fake_order_repository.py
from app.interfaces.repositories.order_repository import OrderRepository
from app.domain.entities.order import Order

class FakeOrderRepository(OrderRepository):

    def __init__(self):
        self.orders: dict[tuple[str,str], Order] = {}

    def get_by_id(self, tenant_id: str, order_id: str) -> Order:
        return self.orders.get((tenant_id, order_id))

    def save(self, order):
        self.orders[(order.tenant_id, order.id)] = order
