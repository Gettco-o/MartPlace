import asyncio

from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_status import CartStatus
from app.domain.value_objects.money import Money
from app.use_cases.cart.add_to_cart import AddToCart
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.helpers import make_buyer

run = asyncio.run


def test_add_to_cart_creates_cart_and_adds_item():
    cart_repo = FakeCartRepository()
    product_repo = FakeProductRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    use_case = AddToCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
    )

    tenant = run(create_tenant.execute(name="Shop A"))
    buyer = make_buyer()
    run(user_repo.save(buyer))
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(2500),
        stock=20,
    )
    run(product_repo.save(product))

    cart = run(use_case.execute(
        actor_user_id=buyer.id,
        user_id=buyer.id,
        tenant_id=tenant.id,
        product_id=product.id,
        quantity=2,
    ))

    assert cart.user_id == buyer.id
    assert len(cart.items) == 1
    assert cart.status == CartStatus.ACTIVE
    assert cart.items[0].product_id == "prod_1"
    assert cart.items[0].quantity == 2
    assert cart.items[0].unit_price == Money(2500)


def test_add_to_cart_merges_same_product_for_same_tenant():
    cart_repo = FakeCartRepository()
    product_repo = FakeProductRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    use_case = AddToCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
    )

    tenant = run(create_tenant.execute(name="Shop A"))
    buyer = make_buyer()
    run(user_repo.save(buyer))
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(2500),
        stock=20,
    )
    run(product_repo.save(product))

    run(use_case.execute(buyer.id, buyer.id, tenant.id, product.id, 2))
    cart = run(use_case.execute(buyer.id, buyer.id, tenant.id, product.id, 3))

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_add_to_cart_rejects_invalid_quantity():
    cart_repo = FakeCartRepository()
    product_repo = FakeProductRepository()
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    use_case = AddToCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
    )
    buyer = make_buyer()
    run(user_repo.save(buyer))

    try:
        run(use_case.execute(buyer.id, buyer.id, "tenant_1", "prod_1", 0))
        raise AssertionError("Expected DomainError")
    except DomainError as exc:
        assert str(exc) == "Quantity must be greater than zero"
