from dataclasses import dataclass, field
from datetime import datetime
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem

@dataclass
class Cart:
    id: str
    user_id: str
    items: list[CartItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: CartItem):
        # Merge if same product + tenant
        for existing in self.items:
            if (
                existing.product_id == item.product_id
                and existing.tenant_id == item.tenant_id
            ):
                self.items.remove(existing)
                self.items.append(
                    CartItem(
                        product_id=existing.product_id,
                        tenant_id=existing.tenant_id,
                        quantity=existing.quantity + item.quantity,
                        unit_price=existing.unit_price
                    )
                )
                return

        self.items.append(item)

    def remove_item(self, product_id: str, tenant_id: str):
        self.items = [
            i for i in self.items
            if not (i.product_id == product_id and i.tenant_id == tenant_id)
        ]

    def clear(self):
        self.items = []

    def is_empty(self) -> bool:
        return len(self.items) == 0