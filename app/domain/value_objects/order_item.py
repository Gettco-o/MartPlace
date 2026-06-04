from dataclasses import dataclass
from app.domain.value_objects.money import Money

@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Money

    def total(self) -> Money:
        return self.unit_price.multiply(self.quantity)