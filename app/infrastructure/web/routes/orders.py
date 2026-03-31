from dataclasses import asdict

from quart import Blueprint
from quart_schema import tag_blueprint, validate_request, validate_response

from app.infrastructure.web.auth import auth_required, get_current_actor_id
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    CreateOrderRequest,
    OrderResponse,
    OrdersResponse,
    OrderSchema,
    RefundOrderRequest,
)
from app.infrastructure.web.utils import success

orders = Blueprint('orders', __name__, url_prefix='/orders')
tag_blueprint(orders, ["orders"])


@orders.get("/<tenant_id>")
@auth_required
@validate_response(OrdersResponse)
async def get_all_orders(tenant_id: str):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        orders_list = await services["get_all_orders"].execute(actor_user_id, tenant_id)

    return success({"orders": [asdict(OrderSchema.from_entity(order)) for order in orders_list]})


@orders.post("/")
@validate_request(CreateOrderRequest)
@auth_required
@validate_response(OrderResponse, 201)
async def create_order(data: CreateOrderRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["create_order"].execute(
            actor_user_id=actor_user_id,
            tenant_id=data.tenant_id,
            user_id=actor_user_id,
            items=[item.to_value_object() for item in data.items],
            idempotency_key=data.idempotency_key,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))}, status_code=201)


@orders.patch("/<tenant_id>/<order_id>/cancel")
@auth_required
@validate_response(OrderResponse)
async def cancel_order(tenant_id: str, order_id: str):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["cancel_order"].execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            order_id=order_id,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))})


@orders.patch("/<tenant_id>/<order_id>/processing")
@auth_required
@validate_response(OrderResponse)
async def start_order_processing(tenant_id: str, order_id: str):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["start_order_processing"].execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            order_id=order_id,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))})


@orders.patch("/<tenant_id>/<order_id>/fulfill")
@auth_required
@validate_response(OrderResponse)
async def fulfill_order(tenant_id: str, order_id: str):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["fulfill_order"].execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            order_id=order_id,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))})


@orders.patch("/<tenant_id>/<order_id>/deliver")
@auth_required
@validate_response(OrderResponse)
async def deliver_order(tenant_id: str, order_id: str):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["deliver_order"].execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            order_id=order_id,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))})


@orders.post("/<tenant_id>/<order_id>/refund")
@validate_request(RefundOrderRequest)
@auth_required
@validate_response(OrderResponse)
async def refund_order(tenant_id: str, order_id: str, data: RefundOrderRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        order = await services["refund_order"].execute(
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            order_id=order_id,
            idempotency_key=data.idempotency_key,
        )
        await services["session"].commit()

    return success({"order": asdict(OrderSchema.from_entity(order))})
