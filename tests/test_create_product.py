import asyncio
import pytest

from app.domain.events.product_created import ProductCreated
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.use_cases.product.create_product import CreateProduct
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.suspend_tenant import SuspendTenant
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.helpers import make_platform_admin, make_tenant_user

run = asyncio.run


def test_create_product_success():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    use_case = CreateProduct(product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute(name="Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))

    product = run(use_case.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        name="Plaster Powder",
        price=Money(1500),
        stock=12,
    ))

    assert product.id is not None
    assert product.tenant_id == tenant.id
    assert product.name == "Plaster Powder"
    assert product.price == Money(1500)
    assert product.stock == 12
    assert run(product_repo.get_by_id(tenant.id, product.id)) == product
    assert any(isinstance(event, ProductCreated) for event in fake_bus.published_events)


def test_create_product_duplicate_name_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    use_case = CreateProduct(product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute(name="Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))

    run(use_case.execute(
        actor_user_id=tenant_user.id,
        tenant_id=tenant.id,
        name="Plaster Powder",
        price=Money(1000),
        stock=10,
    ))

    with pytest.raises(DomainError, match="Product name already in use"):
        run(use_case.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            name="Plaster Powder",
            price=Money(1200),
            stock=5,
        ))


def test_create_product_missing_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    actor = make_tenant_user("tenant-1")
    run(user_repo.save(actor))
    use_case = CreateProduct(product_repo, tenant_repo, user_repo, FakeEventBus())

    with pytest.raises(DomainError, match="Tenant not found"):
        run(use_case.execute(
            actor_user_id=actor.id,
            tenant_id="missing",
            name="Plaster Powder",
            price=Money(1000),
            stock=10,
        ))


def test_create_product_inactive_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    platform_admin = make_platform_admin()
    run(user_repo.save(platform_admin))
    suspend_tenant = SuspendTenant(tenant_repo, user_repo, fake_bus)
    use_case = CreateProduct(product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute(name="Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))
    run(suspend_tenant.execute(platform_admin.id, tenant.id))

    with pytest.raises(DomainError, match="Tenant is not active"):
        run(use_case.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            name="Plaster Powder",
            price=Money(1000),
            stock=10,
        ))


def test_create_product_invalid_values_raise():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo, fake_bus)
    use_case = CreateProduct(product_repo, tenant_repo, user_repo, fake_bus)

    tenant = run(create_tenant.execute(name="Shop A"))
    tenant_user = make_tenant_user(tenant.id)
    run(user_repo.save(tenant_user))

    with pytest.raises(DomainError, match="Product name cannot be empty"):
        run(use_case.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            name="  ",
            price=Money(1000),
            stock=10,
        ))

    with pytest.raises(DomainError, match="Price must be greater than zero"):
        run(use_case.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            name="Plaster Powder",
            price=Money(0),
            stock=10,
        ))

    with pytest.raises(DomainError, match="Stock cannot be negative"):
        run(use_case.execute(
            actor_user_id=tenant_user.id,
            tenant_id=tenant.id,
            name="Plaster Powder",
            price=Money(1000),
            stock=-1,
        ))
