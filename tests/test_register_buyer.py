import pytest
from app.domain.events.buyer_registered import BuyerRegistered
from app.use_cases.user.register_buyer import RegisterBuyer
from tests.fakes.fake_user_repository import FakeUserRepository
from app.domain.exceptions import DomainError
from tests.fakes.fake_event_bus import FakeEventBus


def test_register_buyer_success():
    repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    use_case = RegisterBuyer(repo, fake_bus)

    user = use_case.execute(
        email="buyer@test.com",
        name="Le Buyer",
        password="secure123"
    )

    assert user.email == "buyer@test.com"
    assert user.id is not None
    assert repo.get_by_email("buyer@test.com") == user
    assert any(isinstance(event, BuyerRegistered) for event in fake_bus.published_events)


def test_register_buyer_duplicate_email():
    repo = FakeUserRepository()
    use_case = RegisterBuyer(repo, FakeEventBus())

    use_case.execute(
        email="buyer@test.com",
        name="La Buyer",
        password="secure123"
    )

    with pytest.raises(DomainError):
        use_case.execute(
            email="buyer@test.com",
            name="La Buyer",
            password="another"
        )
