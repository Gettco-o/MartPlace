import asyncio
import pytest

from app.domain.entities.product import Product
from app.domain.events.product_updated import ProductUpdated
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_status import CartStatus
from app.domain.value_objects.money import Money
from app.use_cases.cart.add_to_cart import AddToCart
from app.use_cases.cart.checkout_cart import CheckoutCart
from app.use_cases.product.update_product import UpdateProduct
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.suspend_tenant import SuspendTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer, make_platform_admin, make_tenant_user

run = asyncio.run


def test_update_product_success():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Old Name",
        price=Money(500),
        stock=2,
    )
    run(product_repo.save(product))

    updated = run(update_product.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        product_id="prod_1",
        name="New Name",
        price=Money(1200),
        stock=8,
    ))

    assert updated.id == "prod_1"
    assert updated.name == "New Name"
    assert updated.price == Money(1200)
    assert updated.stock == 8
    assert any(isinstance(event, ProductUpdated) for event in fake_bus.published_events)


def test_update_product_missing_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    actor = make_tenant_user("tenant-1")
    run(user_repo.save(actor))
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, FakeEventBus())

    with pytest.raises(DomainError, match="Tenant not found"):
        run(update_product.execute(
            actor_user_id=actor.id,
            tenant_id="missing",
            product_id="prod_1",
            name="New Name",
            price=Money(1000),
            stock=1,
        ))


def test_update_product_inactive_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    platform_admin = make_platform_admin()
    run(user_repo.save(platform_admin))
    suspend_tenant = SuspendTenant(tenant_repo, user_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))

    run(suspend_tenant.execute(platform_admin.id, tenant.id))

    with pytest.raises(DomainError, match="Tenant is not active"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product B",
            price=Money(1000),
            stock=1,
        ))


def test_update_product_missing_product_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))

    with pytest.raises(DomainError, match="Product not found"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="missing",
            name="Product B",
            price=Money(1000),
            stock=1,
        ))


def test_update_product_duplicate_name_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))
    run(product_repo.save(
        Product(
            id="prod_2",
            tenant_id=tenant.id,
            name="Product B",
            price=Money(1200),
            stock=3,
        )
    ))

    with pytest.raises(DomainError, match="Product name already in use"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product B",
            price=Money(1000),
            stock=1,
        ))


def test_update_product_keeps_same_name_without_false_duplicate():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))

    updated = run(update_product.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        product_id="prod_1",
        name="Product A",
        price=Money(2000),
        stock=5,
    ))

    assert updated.name == "Product A"
    assert updated.price == Money(2000)
    assert updated.stock == 5


def test_update_product_invalid_values_raise():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))

    with pytest.raises(DomainError, match="Product name cannot be empty"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
            name="   ",
            price=Money(1000),
            stock=1,
        ))

    with pytest.raises(DomainError, match="Price must be greater than zero"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product A",
            price=Money(0),
            stock=1,
        ))

    with pytest.raises(DomainError, match="Stock cannot be negative"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
            stock=-1,
        ))


def test_update_product_requires_at_least_one_field():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))

    with pytest.raises(DomainError, match="At least one field must be provided for update"):
        run(update_product.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            product_id="prod_1",
        ))


def test_update_product_allows_partial_stock_only_update():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    ))

    updated = run(update_product.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        product_id="prod_1",
        stock=9,
    ))

    assert updated.name == "Product A"
    assert updated.price == Money(1000)
    assert updated.stock == 9


def test_update_product_refreshes_active_cart_item_prices():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)
    add_to_cart = AddToCart(cart_repo, product_repo, tenant_repo, user_repo)

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    buyer = make_buyer()
    run(user_repo.save(tenant_user))
    run(user_repo.save(buyer))

    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Product A",
        price=Money(1000),
        stock=5,
    )
    run(product_repo.save(product))

    run(add_to_cart.execute(buyer.id, buyer.id, tenant.id, product.id, 2))
    updated = run(update_product.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        product_id="prod_1",
        name="Product A",
        price=Money(1500),
        stock=5,
    ))

    cart = run(cart_repo.get_by_user(buyer.id))
    assert updated.price == Money(1500)
    assert cart.status == CartStatus.ACTIVE
    assert cart.items[0].unit_price == Money(1500)


def test_update_product_does_not_refresh_completed_cart_prices():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    cart_repo = FakeCartRepository()
    order_repo = FakeOrderRepository()
    wallet_repo = FakeWalletRepository()
    idempotency_repo = FakeIdempotencyRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    update_product = UpdateProduct(cart_repo, product_repo, tenant_repo, user_repo, fake_bus)
    add_to_cart = AddToCart(cart_repo, product_repo, tenant_repo, user_repo)
    credit_wallet = CreditWallet(wallet_repo, user_repo, fake_bus)
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

    tenant = run(create_tenant.execute("Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    buyer = make_buyer()
    run(user_repo.save(tenant_user))
    run(user_repo.save(buyer))

    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Product A",
        price=Money(1000),
        stock=5,
    )
    run(product_repo.save(product))

    run(credit_wallet.execute(buyer.id, buyer.id, Money(10000), reference_id="topup-1"))
    run(add_to_cart.execute(buyer.id, buyer.id, tenant.id, product.id, 1))
    run(checkout_cart.execute(buyer.id, buyer.id, "checkout-1"))

    run(update_product.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        product_id="prod_1",
        name="Product A",
        price=Money(2000),
        stock=5,
    ))

    cart = run(cart_repo.get_by_user(buyer.id))
    assert cart.status == CartStatus.COMPLETED
    assert cart.items[0].unit_price == Money(1000)
