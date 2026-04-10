import asyncio

import pytest

from app.domain.entities.cart import Cart
from app.domain.exceptions import DomainError
from app.domain.value_objects.cart_item import CartItem
from app.domain.value_objects.money import Money
from app.use_cases.cart.get_cart import GetCart
from tests.fakes.fake_cart_repository import FakeCartRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.helpers import make_buyer, make_platform_admin

run = asyncio.run


def test_get_cart_returns_authenticated_buyers_cart():
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    buyer = make_buyer()
    run(user_repo.save(buyer))

    cart = Cart(
        id="cart-1",
        user_id=buyer.id,
        items=[
            CartItem(
                product_id="product-1",
                tenant_id="tenant-1",
                quantity=2,
                unit_price=Money(500),
            )
        ],
    )
    run(cart_repo.save(cart))

    result = run(GetCart(cart_repo=cart_repo, user_repo=user_repo).execute(buyer.id, buyer.id))

    assert result == cart


def test_get_cart_rejects_non_buyer_access():
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    admin = make_platform_admin()
    buyer = make_buyer()
    run(user_repo.save(admin))
    run(user_repo.save(buyer))

    with pytest.raises(DomainError, match="User is not a buyer"):
        run(GetCart(cart_repo=cart_repo, user_repo=user_repo).execute(admin.id, buyer.id))


def test_get_cart_raises_when_cart_does_not_exist():
    cart_repo = FakeCartRepository()
    user_repo = FakeUserRepository()
    buyer = make_buyer()
    run(user_repo.save(buyer))

    with pytest.raises(DomainError, match="Cart not found"):
        run(GetCart(cart_repo=cart_repo, user_repo=user_repo).execute(buyer.id, buyer.id))
