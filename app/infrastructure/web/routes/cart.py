from dataclasses import asdict

from quart import Blueprint
from quart_schema import tag_blueprint, validate_request, validate_response

from app.infrastructure.web.auth import auth_required, get_current_actor_id
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    AddToCartRequest,
    CartsResponse,
    CartResponse,
    CartSchema,
    CheckoutCartRequest,
    OrdersResponse,
    OrderSchema,
    RemoveFromCartRequest,
)
from app.infrastructure.web.utils import success

cart = Blueprint('cart', __name__, url_prefix='/cart')
tag_blueprint(cart, ["cart"])


@cart.get("/")
@auth_required
@validate_response(CartsResponse)
async def get_all_carts():
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        carts = await services["get_all_carts"].execute(actor_user_id)

    return success({"carts": [asdict(CartSchema.from_entity(cart_item)) for cart_item in carts]})


@cart.post("/items")
@validate_request(AddToCartRequest)
@auth_required
@validate_response(CartResponse, 201)
async def add_to_cart(data: AddToCartRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        cart_entity = await services["add_to_cart"].execute(
            actor_user_id=actor_user_id,
            user_id=actor_user_id,
            tenant_id=data.tenant_id,
            product_id=data.product_id,
            quantity=data.quantity,
        )
        await services["session"].commit()

    return success({"cart": asdict(CartSchema.from_entity(cart_entity))}, status_code=201)


@cart.delete("/items")
@validate_request(RemoveFromCartRequest)
@auth_required
@validate_response(CartResponse)
async def remove_from_cart(data: RemoveFromCartRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        cart_entity = await services["remove_from_cart"].execute(
            actor_user_id=actor_user_id,
            user_id=actor_user_id,
            tenant_id=data.tenant_id,
            product_id=data.product_id,
        )
        await services["session"].commit()

    return success({"cart": asdict(CartSchema.from_entity(cart_entity))})


@cart.post("/checkout")
@validate_request(CheckoutCartRequest)
@auth_required
@validate_response(OrdersResponse, 201)
async def checkout_cart(data: CheckoutCartRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        orders = await services["checkout_cart"].execute(
            actor_user_id=actor_user_id,
            user_id=actor_user_id,
            idempotency_key=data.idempotency_key,
        )
        await services["session"].commit()

    return success(
        {"orders": [asdict(OrderSchema.from_entity(order)) for order in orders]},
        status_code=201,
    )
