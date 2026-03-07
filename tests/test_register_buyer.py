import pytest
from app.use_cases.user.register_buyer import RegisterBuyer
from tests.fakes.fake_user_repository import FakeUserRepository
from app.domain.exceptions import DomainError


def test_register_buyer_success():
    repo = FakeUserRepository()
    use_case = RegisterBuyer(repo)

    user = use_case.execute(
        email="buyer@test.com",
        name="Le Buyer",
        password="secure123"
    )

    assert user.email == "buyer@test.com"
    assert user.id is not None
    assert repo.get_by_email("buyer@test.com") == user


def test_register_buyer_duplicate_email():
    repo = FakeUserRepository()
    use_case = RegisterBuyer(repo)

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