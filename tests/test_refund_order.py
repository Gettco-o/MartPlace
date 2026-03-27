import asyncio

from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.domain.value_objects.order_status import OrderStatus
from app.use_cases.order.create_order import CreateOrder
from app.use_cases.order.refund_order import RefundOrder
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_event_bus import FakeEventBus
from app.domain.events.order_refunded import OrderRefunded
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer

run = asyncio.run


def test_refund_order_idempotent():
    # repositories
    wallet_repo = FakeWalletRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    idem_repo = FakeIdempotencyRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()

    # use cases
    fake_bus = FakeEventBus()
    credit_wallet = CreditWallet(wallet_repo, user_repo, fake_bus)
    create_order = CreateOrder(
        order_repo,
        product_repo,
        wallet_repo,
        idem_repo,
        tenant_repo,
        user_repo,
        fake_bus,
    )
    refund_order = RefundOrder(
        order_repo,
        product_repo,
        wallet_repo,
        idem_repo,
        tenant_repo,
        user_repo,
        fake_bus,
    )

    create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

    tenant = run(create_tenant_use_case.execute(name="Shop A"))
    buyer = make_buyer()
    run(user_repo.save(buyer))

    # setup product
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Nunex",
        price=Money(50),
        stock=10,
    )
    run(product_repo.save(product))

    # setup wallet
    run(credit_wallet.execute(buyer.id, buyer.id, Money(100)))

    # create order
    order = run(create_order.execute(
            actor_user_id=buyer.id,
            tenant_id=tenant.id,
            user_id=buyer.id,
            items=[
                  OrderItem(
                        product_id="prod_1",
                        quantity=2,
                        unit_price=Money(50)
                  )
            ],
            idempotency_key="order-123"))

    # refund (first call)
    refunded_1 = run(refund_order.execute(
        actor_user_id=buyer.id,
        tenant_id=tenant.id,
        order_id=order.id,
        idempotency_key="refund-123",
    ))

    # refund (retry)
    refunded_2 = run(refund_order.execute(
        actor_user_id=buyer.id,
        tenant_id=tenant.id,
        order_id=order.id,
        idempotency_key="refund-123",
    ))

    # assertions
    assert refunded_1.id == refunded_2.id
    assert refunded_1.status == OrderStatus.REFUNDED
    # ensure an OrderRefunded event was published
    assert any(isinstance(e, OrderRefunded) for e in fake_bus.published_events)

    wallet = run(wallet_repo.get_wallet(buyer.id))
    assert wallet.balance.amount == 100  # refunded

    product = run(product_repo.get_by_id(tenant.id, "prod_1"))
    assert product.stock == 10  # stock restored
