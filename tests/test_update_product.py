import pytest

from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.use_cases.product.update_product import UpdateProduct
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.tenant.suspend_tenant import SuspendTenant
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository


def test_update_product_success():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Old Name",
        price=Money(500),
        stock=2,
    )
    product_repo.save(product)

    updated = update_product.execute(
        tenant_id=tenant.id,
        product_id="prod_1",
        name="New Name",
        price=Money(1200),
        stock=8,
    )

    assert updated.id == "prod_1"
    assert updated.name == "New Name"
    assert updated.price == Money(1200)
    assert updated.stock == 8


def test_update_product_missing_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()
    update_product = UpdateProduct(product_repo, tenant_repo)

    with pytest.raises(DomainError, match="Tenant not found"):
        update_product.execute(
            tenant_id="missing",
            product_id="prod_1",
            name="New Name",
            price=Money(1000),
            stock=1,
        )


def test_update_product_inactive_tenant_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    suspend_tenant = SuspendTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")
    product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    )

    suspend_tenant.execute(tenant.id)

    with pytest.raises(DomainError, match="Tenant is not active"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product B",
            price=Money(1000),
            stock=1,
        )


def test_update_product_missing_product_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")

    with pytest.raises(DomainError, match="Product not found"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="missing",
            name="Product B",
            price=Money(1000),
            stock=1,
        )


def test_update_product_duplicate_name_raises():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")
    product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    )
    product_repo.save(
        Product(
            id="prod_2",
            tenant_id=tenant.id,
            name="Product B",
            price=Money(1200),
            stock=3,
        )
    )

    with pytest.raises(DomainError, match="Product name already in use"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product B",
            price=Money(1000),
            stock=1,
        )


def test_update_product_keeps_same_name_without_false_duplicate():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")
    product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    )

    updated = update_product.execute(
        tenant_id=tenant.id,
        product_id="prod_1",
        name="Product A",
        price=Money(2000),
        stock=5,
    )

    assert updated.name == "Product A"
    assert updated.price == Money(2000)
    assert updated.stock == 5


def test_update_product_invalid_values_raise():
    tenant_repo = FakeTenantRepository()
    product_repo = FakeProductRepository()

    create_tenant = CreateTenant(tenant_repo)
    update_product = UpdateProduct(product_repo, tenant_repo)

    tenant = create_tenant.execute("Shop A")
    product_repo.save(
        Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Product A",
            price=Money(1000),
            stock=1,
        )
    )

    with pytest.raises(DomainError, match="Product name cannot be empty"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="prod_1",
            name="   ",
            price=Money(1000),
            stock=1,
        )

    with pytest.raises(DomainError, match="Price must be greater than zero"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product A",
            price=Money(0),
            stock=1,
        )

    with pytest.raises(DomainError, match="Stock cannot be negative"):
        update_product.execute(
            tenant_id=tenant.id,
            product_id="prod_1",
            name="Product A",
            price=Money(1000),
            stock=-1,
        )
