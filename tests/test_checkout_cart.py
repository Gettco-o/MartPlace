from app.domain.entities.product import Product
from app.domain.events.order_created import OrderCreated
from app.domain.events.wallet_debited import WalletDebited
from app.domain.value_objects.money import Money
from app.use_cases.cart.add_to_cart import AddToCart
from app.use_cases.cart.checkout_cart import CheckoutCart
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer


def test_checkout_cart_creates_order_debits_wallet_and_clears_cart():
    cart_repo = FakeCartRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    wallet_repo = FakeWalletRepository()
    idempotency_repo = FakeIdempotencyRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    add_to_cart = AddToCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
    )
    credit_wallet = CreditWallet(
        wallet_repository=wallet_repo,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        event_bus=fake_bus,
    )
    checkout_cart = CheckoutCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        order_repo=order_repo,
        wallet_repo=wallet_repo,
        idempotency_repo=idempotency_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
        event_bus=fake_bus,
    )

    tenant = create_tenant.execute(name="Shop A")
    buyer = make_buyer()
    user_repo.save(buyer)
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(5000),
        stock=10,
    )
    product_repo.save(product)

    credit_wallet.execute(buyer.id, tenant.id, buyer.id, Money(15000), reference_id="topup-1")
    add_to_cart.execute(buyer.id, buyer.id, tenant.id, product.id, 2)

    orders = checkout_cart.execute(actor_user_id=buyer.id, user_id=buyer.id, idempotency_key="checkout-123")

    assert len(orders) == 1
    assert orders[0].tenant_id == tenant.id
    assert orders[0].amount == Money(10000)
    assert wallet_repo.get_wallet(tenant.id, buyer.id).balance == Money(5000)
    assert wallet_repo.has_reference(tenant.id, buyer.id, orders[0].id)
    assert product_repo.get_by_id(tenant.id, product.id).stock == 8
    assert cart_repo.get_by_user(buyer.id).is_empty()
    assert any(isinstance(event, WalletDebited) for event in fake_bus.published_events)
    assert any(isinstance(event, OrderCreated) for event in fake_bus.published_events)
