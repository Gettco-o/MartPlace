from app.domain.entities.cart import Cart
from app.domain.value_objects.cart_item import CartItem
from app.domain.value_objects.cart_status import CartStatus
from app.domain.value_objects.money import Money
from app.infrastructure.db.mappers import cart_to_model
from app.infrastructure.db.models import CartItemModel, CartModel


def test_cart_to_model_reuses_existing_item_models_for_same_product_and_tenant():
    existing_item = CartItemModel(
        product_id="product-1",
        tenant_id="tenant-1",
        quantity=1,
        unit_price_amount=250000,
    )
    model = CartModel(
        id="cart-1",
        user_id="buyer-1",
        status=CartStatus.ACTIVE,
    )
    model.items = [existing_item]

    entity = Cart(
        id="cart-1",
        user_id="buyer-1",
        status=CartStatus.COMPLETED,
        items=[
            CartItem(
                product_id="product-1",
                tenant_id="tenant-1",
                quantity=1,
                unit_price=Money(250000),
            )
        ],
    )

    updated_model = cart_to_model(entity, model)

    assert updated_model.status == CartStatus.COMPLETED
    assert len(updated_model.items) == 1
    assert updated_model.items[0] is existing_item
    assert updated_model.items[0].quantity == 1
    assert updated_model.items[0].unit_price_amount == 250000
