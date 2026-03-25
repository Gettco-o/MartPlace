from app.domain.entities.product import Product
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.use_cases.cart.add_to_cart import AddToCart
from app.use_cases.cart.remove_from_cart import RemoveFromCart
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository


def test_remove_from_cart_removes_existing_item():
    cart_repo = FakeCartRepository()
    product_repo = FakeProductRepository()
    tenant_repo = FakeTenantRepository()
    fake_bus = FakeEventBus()

    create_tenant = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
    add_to_cart = AddToCart(
        cart_repo=cart_repo,
        product_repo=product_repo,
        tenant_repo=tenant_repo,
    )
    remove_from_cart = RemoveFromCart(cart_repo=cart_repo)

    tenant = create_tenant.execute(name="Shop A")
    product = Product(
        id="prod_1",
        tenant_id=tenant.id,
        name="Rice",
        price=Money(2500),
        stock=20,
    )
    product_repo.save(product)

    add_to_cart.execute("user_1", tenant.id, product.id, 2)
    cart = remove_from_cart.execute("user_1", tenant.id, product.id)

    assert cart.is_empty()


def test_remove_from_cart_rejects_missing_item():
    cart_repo = FakeCartRepository()
    remove_from_cart = RemoveFromCart(cart_repo=cart_repo)

    try:
        remove_from_cart.execute("user_1", "tenant_1", "prod_1")
        raise AssertionError("Expected DomainError")
    except DomainError as exc:
        assert str(exc) == "Cart not found"
