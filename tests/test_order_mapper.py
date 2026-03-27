from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.domain.value_objects.order_status import OrderStatus
from app.infrastructure.db.mappers import order_to_model
from app.infrastructure.db.models import OrderItemModel, OrderModel


def test_order_to_model_reuses_existing_item_models_for_same_product():
    existing_item = OrderItemModel(
        product_id="product-1",
        quantity=5,
        unit_price_amount=250000,
    )
    model = OrderModel(
        id="order-1",
        tenant_id="tenant-1",
        user_id="buyer-1",
        amount=1250000,
        status=OrderStatus.PAID,
    )
    model.items = [existing_item]

    entity = Order(
        id="order-1",
        tenant_id="tenant-1",
        user_id="buyer-1",
        items=[
            OrderItem(
                product_id="product-1",
                quantity=5,
                unit_price=Money(250000),
            )
        ],
        amount=Money(1250000),
        status=OrderStatus.CANCELLED,
    )

    updated_model = order_to_model(entity, model)

    assert updated_model.status == OrderStatus.CANCELLED
    assert len(updated_model.items) == 1
    assert updated_model.items[0] is existing_item
    assert updated_model.items[0].quantity == 5
    assert updated_model.items[0].unit_price_amount == 250000
