from dataclasses import dataclass

from app.domain.entities.cart import Cart


@dataclass
class AddToCartRequest:
    tenant_id: str
    product_id: str
    quantity: int


@dataclass
class RemoveFromCartRequest:
    tenant_id: str
    product_id: str


@dataclass
class CheckoutCartRequest:
    idempotency_key: str


@dataclass
class CartItemSchema:
    product_id: str
    tenant_id: str
    quantity: int
    unit_price_amount: int


@dataclass
class CartSchema:
    id: str
    user_id: str
    status: str
    items: list[CartItemSchema]

    @classmethod
    def from_entity(cls, cart: Cart) -> "CartSchema":
        return cls(
            id=cart.id,
            user_id=cart.user_id,
            status=cart.status.value,
            items=[
                CartItemSchema(
                    product_id=item.product_id,
                    tenant_id=item.tenant_id,
                    quantity=item.quantity,
                    unit_price_amount=item.unit_price.amount,
                )
                for item in cart.items
            ],
        )


@dataclass
class CartResponse:
    success: bool
    cart: CartSchema
