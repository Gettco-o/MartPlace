from dataclasses import asdict

from quart import Blueprint
from quart_schema import validate_request, validate_response

from app.domain.value_objects.money import Money
from app.infrastructure.web.auth import auth_required, get_current_actor_id
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    CreateProductRequest,
    ProductResponse,
    ProductSchema,
)
from app.infrastructure.web.utils import success

products = Blueprint('products', __name__, url_prefix='/products')


@products.post("/")
@validate_request(CreateProductRequest)
@auth_required
@validate_response(ProductResponse, 201)
async def create_product(data: CreateProductRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        product = await services["create_product"].execute(
            actor_user_id=actor_user_id,
            tenant_id=data.tenant_id,
            name=data.name,
            price=Money(data.price_amount),
            stock=data.stock,
        )
        await services["session"].commit()

    return success({"product": asdict(ProductSchema.from_entity(product))}, status_code=201)


@products.get("/<tenant_id>/<product_id>")
@validate_response(ProductResponse)
async def get_product(tenant_id: str, product_id: str):
    async with request_services() as services:
        product = await services["get_product"].execute(tenant_id, product_id)

    return success({"product": asdict(ProductSchema.from_entity(product))})
