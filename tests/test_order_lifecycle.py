import asyncio
import pytest

from app.domain.entities.product import Product
from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_fulfilled import OrderFulfilled
from app.domain.events.order_processing_started import OrderProcessingStarted
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.domain.value_objects.order_status import OrderStatus
from app.use_cases.order.cancel_order import CancelOrder
from app.use_cases.order.create_order import CreateOrder
from app.use_cases.order.deliver_order import DeliverOrder
from app.use_cases.order.fulfill_order import FulfillOrder
from app.use_cases.order.start_order_processing import StartOrderProcessing
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_tenant_wallet_repository import FakeTenantWalletRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer, make_tenant_user

run = asyncio.run


def test_order_progresses_from_paid_to_processing_to_fulfilled_to_delivered():
    wallet_repo = FakeWalletRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    idem_repo = FakeIdempotencyRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    tenant_wallet_repo = FakeTenantWalletRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
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
    start_processing = StartOrderProcessing(order_repo, tenant_repo, user_repo, fake_bus)
    fulfill_order = FulfillOrder(order_repo, tenant_repo, user_repo, fake_bus)
    deliver_order = DeliverOrder(order_repo, tenant_repo, tenant_wallet_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute(name="Shop A"))
    buyer = make_buyer()
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(buyer))
    run(user_repo.save(tenant_user))

    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(5000),
        stock=10,
    )
    run(product_repo.save(product))

    run(credit_wallet.execute(buyer.id, buyer.id, Money(15000), reference_id="topup-1"))
    order = run(create_order.execute(
        actor_user_id=buyer.id,
        tenant_id=tenant.id,
        user_id=buyer.id,
        items=[OrderItem(product_id=product.id, quantity=2, unit_price=Money(1))],
        idempotency_key="order-1",
    ))

    processing = run(start_processing.execute(tenant_user.id, tenant.id, order.id))
    assert processing.status == OrderStatus.PROCESSING

    fulfilled = run(fulfill_order.execute(tenant_user.id, tenant.id, order.id))
    assert fulfilled.status == OrderStatus.FULFILLED

    delivered = run(deliver_order.execute(tenant_user.id, tenant.id, order.id))
    assert delivered.status == OrderStatus.DELIVERED
    assert run(tenant_wallet_repo.get_wallet(tenant.id)).balance == Money(10000)
    assert any(isinstance(e, OrderProcessingStarted) for e in fake_bus.published_events)
    assert any(isinstance(e, OrderFulfilled) for e in fake_bus.published_events)
    assert any(isinstance(e, OrderDelivered) for e in fake_bus.published_events)


def test_buyer_can_cancel_paid_order_and_get_wallet_refund_and_stock_back():
    wallet_repo = FakeWalletRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    idem_repo = FakeIdempotencyRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    tenant_wallet_repo = FakeTenantWalletRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
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
    cancel_order = CancelOrder(
        order_repo,
        product_repo,
        wallet_repo,
        tenant_repo,
        user_repo,
        fake_bus,
    )

    tenant = run(create_tenant.execute(name="Shop A"))
    buyer = make_buyer()
    run(user_repo.save(buyer))

    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(5000),
        stock=10,
    )
    run(product_repo.save(product))

    run(credit_wallet.execute(buyer.id, buyer.id, Money(15000), reference_id="topup-1"))
    order = run(create_order.execute(
        actor_user_id=buyer.id,
        tenant_id=tenant.id,
        user_id=buyer.id,
        items=[OrderItem(product_id=product.id, quantity=1, unit_price=Money(1))],
        idempotency_key="order-2",
    ))

    cancelled = run(cancel_order.execute(buyer.id, tenant.id, order.id))

    assert cancelled.status == OrderStatus.CANCELLED
    assert run(wallet_repo.get_wallet(buyer.id)).balance == Money(15000)
    assert run(tenant_wallet_repo.get_wallet(tenant.id)) is None
    assert run(product_repo.get_by_id(tenant.id, product.id)).stock == 10
    assert any(isinstance(e, OrderCancelled) for e in fake_bus.published_events)


def test_order_rejects_invalid_lifecycle_transitions():
    wallet_repo = FakeWalletRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    idem_repo = FakeIdempotencyRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    tenant_wallet_repo = FakeTenantWalletRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
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
    start_processing = StartOrderProcessing(order_repo, tenant_repo, user_repo, fake_bus)
    fulfill_order = FulfillOrder(order_repo, tenant_repo, user_repo, fake_bus)
    deliver_order = DeliverOrder(order_repo, tenant_repo, tenant_wallet_repo, user_repo, fake_bus)
    cancel_order = CancelOrder(
        order_repo,
        product_repo,
        wallet_repo,
        tenant_repo,
        user_repo,
        fake_bus,
    )

    tenant = run(create_tenant.execute(name="Shop A"))
    buyer = make_buyer()
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(buyer))
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Rice",
            price=Money(5000),
            stock=10,
        )
    ))

    run(credit_wallet.execute(buyer.id, buyer.id, Money(20000), reference_id="topup-1"))
    order = run(create_order.execute(
        actor_user_id=buyer.id,
        tenant_id=tenant.id,
        user_id=buyer.id,
        items=[OrderItem(product_id="prod_1", quantity=1, unit_price=Money(1))],
        idempotency_key="order-invalid-1",
    ))

    with pytest.raises(DomainError, match="Only processing orders can be marked as FULFILLED"):
        run(fulfill_order.execute(tenant_user.id, tenant.id, order.id))

    with pytest.raises(DomainError, match="Only fulfilled orders can be marked as DELIVERED"):
        run(deliver_order.execute(tenant_user.id, tenant.id, order.id))

    run(start_processing.execute(tenant_user.id, tenant.id, order.id))

    with pytest.raises(DomainError, match="Only paid orders can be cancelled"):
        run(cancel_order.execute(buyer.id, tenant.id, order.id))
