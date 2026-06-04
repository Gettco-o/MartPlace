import asyncio

import pytest

from app.domain.entities.cart import Cart
from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.use_cases.cart.get_all_carts import GetAllCarts
from app.use_cases.order.get_all_orders import GetAllOrders
from app.use_cases.product.get_all_products import GetAllProducts
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.get_active_tenants import GetActiveTenants
from app.use_cases.tenant.get_all_tenants import GetAllTenants
from app.use_cases.tenant.suspend_tenant import SuspendTenant
from app.use_cases.user.get_all_users import GetAllUsers
from app.use_cases.wallet.credit_wallet import CreditWallet
from app.use_cases.wallet.get_all_wallets import GetAllWallets
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer, make_platform_admin, make_tenant_user

run = asyncio.run


def test_get_all_products_returns_products_for_tenant():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    tenant = run(create_tenant.execute(name="Shop A"))
    other_tenant = run(create_tenant.execute(name="Shop B"))

    product_a = product_repo.products.setdefault(
        (tenant.id, "product-1"),
        Product(
            id="product-1",
            tenant_id=tenant.id,
            name="Item A",
            price=Money(1000),
            stock=5,
        ),
    )
    product_b = product_repo.products.setdefault(
        (other_tenant.id, "product-2"),
        Product(
            id="product-2",
            tenant_id=other_tenant.id,
            name="Item B",
            price=Money(2000),
            stock=8,
        ),
    )

    use_case = GetAllProducts(product_repo=product_repo, tenant_repo=tenant_repo)

    products = run(use_case.execute(tenant.id))

    assert products == [product_a]
    assert product_b not in products


def test_get_all_products_feed_returns_only_products_from_active_tenants():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    active_tenant = run(create_tenant.execute(name="Shop A"))
    suspended_tenant = run(create_tenant.execute(name="Shop B"))

    admin = make_platform_admin()
    run(user_repo.save(admin))
    run(SuspendTenant(tenant_repo=tenant_repo, user_repo=user_repo, event_bus=fake_bus).execute(admin.id, suspended_tenant.id))

    active_product = Product(
        id="product-1",
        tenant_id=active_tenant.id,
        name="Visible Item",
        price=Money(1000),
        stock=5,
    )
    hidden_product = Product(
        id="product-2",
        tenant_id=suspended_tenant.id,
        name="Hidden Item",
        price=Money(2000),
        stock=8,
    )
    run(product_repo.save(active_product))
    run(product_repo.save(hidden_product))

    products = run(GetAllProducts(product_repo=product_repo, tenant_repo=tenant_repo).execute())

    assert products == [active_product]
    assert hidden_product not in products


def test_get_all_tenants_requires_platform_admin():
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    run(create_tenant.execute(name="Shop A"))

    buyer = make_buyer()
    run(user_repo.save(buyer))

    use_case = GetAllTenants(tenant_repo=tenant_repo, user_repo=user_repo)

    with pytest.raises(DomainError, match="User is not a platform admin"):
        run(use_case.execute(buyer.id))


def test_get_active_tenants_returns_only_active_tenants():
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    active_tenant = run(create_tenant.execute(name="Shop A"))
    suspended_tenant = run(create_tenant.execute(name="Shop B"))

    admin = make_platform_admin()
    run(user_repo.save(admin))
    run(SuspendTenant(tenant_repo=tenant_repo, user_repo=user_repo, event_bus=fake_bus).execute(admin.id, suspended_tenant.id))

    tenants = run(GetActiveTenants(tenant_repo=tenant_repo).execute())

    assert tenants == [active_tenant]
    assert suspended_tenant not in tenants


def test_get_all_users_returns_users_for_platform_admin():
    user_repo = FakeUserRepository()
    admin = make_platform_admin()
    buyer = make_buyer()
    run(user_repo.save(admin))
    run(user_repo.save(buyer))

    users = run(GetAllUsers(user_repo=user_repo).execute(admin.id))

    assert {user.id for user in users} == {admin.id, buyer.id}


def test_get_all_orders_requires_tenant_membership():
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    order_repo = FakeOrderRepository()
    fake_bus = FakeEventBus()
    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    tenant = run(create_tenant.execute(name="Shop A"))

    actor = make_tenant_user("other-tenant")
    run(user_repo.save(actor))

    use_case = GetAllOrders(
        order_repo=order_repo,
        tenant_repo=tenant_repo,
        user_repo=user_repo,
    )

    with pytest.raises(DomainError, match="User does not belong to this tenant"):
        run(use_case.execute(actor.id, tenant.id))


def test_get_all_orders_returns_orders_for_tenant_manager():
    tenant_repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    order_repo = FakeOrderRepository()
    fake_bus = FakeEventBus()
    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    tenant = run(create_tenant.execute(name="Shop A"))

    actor = make_tenant_user(tenant.id)
    run(user_repo.save(actor))

    order = Order(
        id="order-1",
        tenant_id=tenant.id,
        user_id="buyer-1",
        items=[OrderItem(product_id="product-1", quantity=2, unit_price=Money(500))],
        amount=Money(1000),
    )
    run(order_repo.save(order))

    orders = run(
        GetAllOrders(
            order_repo=order_repo,
            tenant_repo=tenant_repo,
            user_repo=user_repo,
        ).execute(actor.id, tenant.id)
    )

    assert orders == [order]


def test_get_all_carts_requires_platform_admin():
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    buyer = make_buyer()
    run(user_repo.save(buyer))

    run(
        cart_repo.save(
            Cart(
                id="cart-1",
                user_id=buyer.id,
                items=[
                    CartItem(
                        product_id="product-1",
                        tenant_id="tenant-1",
                        quantity=1,
                        unit_price=Money(500),
                    )
                ],
            )
        )
    )

    with pytest.raises(DomainError, match="User is not a platform admin"):
        run(GetAllCarts(cart_repo=cart_repo, user_repo=user_repo).execute(buyer.id))


def test_get_all_wallets_returns_wallets_for_platform_admin():
    wallet_repo = FakeWalletRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    admin = make_platform_admin()
    buyer = make_buyer()
    run(user_repo.save(admin))
    run(user_repo.save(buyer))

    run(
        CreditWallet(
            wallet_repository=wallet_repo,
            user_repository=user_repo,
            event_bus=fake_bus,
        ).execute(
            actor_user_id=buyer.id,
            user_id=buyer.id,
            amount=Money(1500),
            reference_id="wallet-topup-1",
        )
    )

    wallets = run(
        GetAllWallets(
            wallet_repository=wallet_repo,
            user_repository=user_repo,
        ).execute(admin.id)
    )

    assert len(wallets) == 1
    assert wallets[0].user_id == buyer.id
    assert wallets[0].balance == Money(1500)
