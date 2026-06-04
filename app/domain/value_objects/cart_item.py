from dataclasses import dataclass
from datetime import datetime
from app.domain.value_objects.money import Money

@dataclass(frozen=True)
class CartItem:
    product_id: str
    tenant_id: str
    quantity: int
    unit_price: Money   # price snapshot