from contextlib import asynccontextmanager

from quart import current_app

from app.infrastructure.db.repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemyTenantRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.db.repositories.cart_repository import SqlAlchemyCartRepository
from app.use_cases.product.create_product import CreateProduct
from app.use_cases.product.get_product import GetProduct
from app.use_cases.product.update_product import UpdateProduct
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.get_tenant import GetTenant
from app.use_cases.user.authenticate_user import AuthenticateUser
from app.use_cases.user.get_user import GetUser
from app.use_cases.user.register_buyer import RegisterBuyer
from app.use_cases.user.register_tenant_user import RegisterTenantUser


@asynccontextmanager
async def request_services():
    db = current_app.extensions["db"]
    event_bus = current_app.extensions["event_bus"]

    async with db.session() as session:
        tenant_repo = SqlAlchemyTenantRepository(session)
        user_repo = SqlAlchemyUserRepository(session)
        product_repo = SqlAlchemyProductRepository(session)
        cart_repo = SqlAlchemyCartRepository(session)

        yield {
            "session": session,
            "create_tenant": CreateTenant(
                tenant_repo=tenant_repo,
                event_bus=event_bus,
                user_repo=user_repo,
            ),
            "get_tenant": GetTenant(tenant_repo=tenant_repo),
            "register_buyer": RegisterBuyer(
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "authenticate_user": AuthenticateUser(user_repo=user_repo),
            "register_tenant_user": RegisterTenantUser(
                user_repo=user_repo,
                tenant_repo=tenant_repo,
                event_bus=event_bus,
            ),
            "get_user": GetUser(user_repo=user_repo),
            "create_product": CreateProduct(
                product_repo=product_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "get_product": GetProduct(product_repo=product_repo),
            "update_product": UpdateProduct(
                cart_repo=cart_repo,
                product_repo=product_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus
            )
        }
