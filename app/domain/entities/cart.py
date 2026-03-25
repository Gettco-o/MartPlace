from dataclasses import dataclass, field
from datetime import datetime
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem
from app.domain.value_objects.cart_status import CartStatus

@dataclass
class Cart:
    id: str
    user_id: str
    items: list[CartItem] = field(default_factory=list)
    status: CartStatus = CartStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: CartItem):
        self.ensure_active()

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
                        unit_price=item.unit_price,
                    )
                )
                return

        self.items.append(item)

    def remove_item(self, product_id: str, tenant_id: str):
        self.ensure_active()
        self.items = [
            i for i in self.items
            if not (i.product_id == product_id and i.tenant_id == tenant_id)
        ]

    def refresh_item_price(self, product_id: str, tenant_id: str, unit_price):
        if self.status != CartStatus.ACTIVE:
            return

        refreshed_items = []
        for item in self.items:
            if item.product_id == product_id and item.tenant_id == tenant_id:
                refreshed_items.append(
                    CartItem(
                        product_id=item.product_id,
                        tenant_id=item.tenant_id,
                        quantity=item.quantity,
                        unit_price=unit_price,
                    )
                )
            else:
                refreshed_items.append(item)

        self.items = refreshed_items

    def complete(self):
        self.ensure_active()
        self.status = CartStatus.COMPLETED

    def ensure_active(self):
        if self.status != CartStatus.ACTIVE:
            raise DomainError("Cart is already completed")

    def is_empty(self) -> bool:
        return len(self.items) == 0
