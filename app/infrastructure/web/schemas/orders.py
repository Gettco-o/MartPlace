from dataclasses import dataclass

from app.domain.entities.order import Order
from app.domain.value_objects.order_item import OrderItem


@dataclass
class OrderItemRequest:
    product_id: str
    quantity: int
    unit_price_amount: int

    def to_value_object(self) -> OrderItem:
        from app.domain.value_objects.money import Money

        return OrderItem(
            product_id=self.product_id,
            quantity=self.quantity,
            unit_price=Money(self.unit_price_amount),
        )


@dataclass
class CreateOrderRequest:
    tenant_id: str
    items: list[OrderItemRequest]
    idempotency_key: str


@dataclass
class RefundOrderRequest:
    idempotency_key: str


@dataclass
class OrderItemSchema:
    product_id: str
    quantity: int
    unit_price_amount: int


@dataclass
class OrderSchema:
    id: str
    tenant_id: str
    user_id: str
    amount: int
    status: str
    items: list[OrderItemSchema]

    @classmethod
    def from_entity(cls, order: Order) -> "OrderSchema":
        return cls(
            id=order.id,
            tenant_id=order.tenant_id,
            user_id=order.user_id,
            amount=order.amount.amount,
            status=order.status.value,
            items=[
                OrderItemSchema(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price_amount=item.unit_price.amount,
                )
                for item in order.items
            ],
        )


@dataclass
class OrderResponse:
    success: bool
    order: OrderSchema


@dataclass
class OrdersResponse:
    success: bool
    orders: list[OrderSchema]
