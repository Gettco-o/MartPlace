from contextlib import asynccontextmanager

from quart import current_app

from app.infrastructure.db.repositories import (
    SqlAlchemyCartRepository,
    SqlAlchemyIdempotencyRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
    SqlAlchemyTenantRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyWalletRepository,
)
from app.use_cases.cart.add_to_cart import AddToCart
from app.use_cases.cart.checkout_cart import CheckoutCart
from app.use_cases.cart.remove_from_cart import RemoveFromCart
from app.use_cases.order.cancel_order import CancelOrder
from app.use_cases.order.create_order import CreateOrder
from app.use_cases.order.deliver_order import DeliverOrder
from app.use_cases.order.fulfill_order import FulfillOrder
from app.use_cases.order.refund_order import RefundOrder
from app.use_cases.order.start_order_processing import StartOrderProcessing
from app.use_cases.product.create_product import CreateProduct
from app.use_cases.product.get_product import GetProduct
from app.use_cases.product.update_product import UpdateProduct
from app.use_cases.tenant.activate_tenant import ActivateTenant
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.get_tenant import GetTenant
from app.use_cases.tenant.suspend_tenant import SuspendTenant
from app.use_cases.user.authenticate_user import AuthenticateUser
from app.use_cases.user.get_user import GetUser
from app.use_cases.user.register_buyer import RegisterBuyer
from app.use_cases.user.register_tenant_user import RegisterTenantUser
from app.use_cases.wallet.credit_wallet import CreditWallet
from app.use_cases.wallet.debit_wallet import DebitWallet


@asynccontextmanager
async def request_services():
    db = current_app.extensions["db"]
    event_bus = current_app.extensions["event_bus"]

    async with db.session() as session:
        tenant_repo = SqlAlchemyTenantRepository(session)
        user_repo = SqlAlchemyUserRepository(session)
        product_repo = SqlAlchemyProductRepository(session)
        cart_repo = SqlAlchemyCartRepository(session)
        order_repo = SqlAlchemyOrderRepository(session)
        wallet_repo = SqlAlchemyWalletRepository(session)
        idempotency_repo = SqlAlchemyIdempotencyRepository(session)

        yield {
            "session": session,
            "create_tenant": CreateTenant(
                tenant_repo=tenant_repo,
                event_bus=event_bus,
                user_repo=user_repo,
            ),
            "get_tenant": GetTenant(tenant_repo=tenant_repo),
            "activate_tenant": ActivateTenant(
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus
            ),
            "suspend_tenant": SuspendTenant(
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus
            ),
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
                event_bus=event_bus,
            ),
            "add_to_cart": AddToCart(
                cart_repo=cart_repo,
                product_repo=product_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
            ),
            "remove_from_cart": RemoveFromCart(
                cart_repo=cart_repo,
                user_repo=user_repo,
            ),
            "checkout_cart": CheckoutCart(
                cart_repo=cart_repo,
                product_repo=product_repo,
                order_repo=order_repo,
                wallet_repo=wallet_repo,
                idempotency_repo=idempotency_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "create_order": CreateOrder(
                order_repo=order_repo,
                product_repo=product_repo,
                wallet_repo=wallet_repo,
                idempotency_repo=idempotency_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "cancel_order": CancelOrder(
                order_repo=order_repo,
                product_repo=product_repo,
                wallet_repo=wallet_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "start_order_processing": StartOrderProcessing(
                order_repo=order_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "fulfill_order": FulfillOrder(
                order_repo=order_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "deliver_order": DeliverOrder(
                order_repo=order_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "refund_order": RefundOrder(
                order_repo=order_repo,
                product_repo=product_repo,
                wallet_repo=wallet_repo,
                idempotency_repo=idempotency_repo,
                tenant_repo=tenant_repo,
                user_repo=user_repo,
                event_bus=event_bus,
            ),
            "credit_wallet": CreditWallet(
                wallet_repository=wallet_repo,
                user_repository=user_repo,
                event_bus=event_bus,
            ),
            "debit_wallet": DebitWallet(
                wallet_repository=wallet_repo,
                user_repository=user_repo,
                event_bus=event_bus,
            ),
        }
