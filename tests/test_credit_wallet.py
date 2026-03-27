import asyncio

from app.domain.events.wallet_credited import WalletCredited
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from app.domain.value_objects.money import Money
from tests.helpers import make_buyer

run = asyncio.run

def test_credit_wallet():
    # Arrange
    wallet_repo = FakeWalletRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    use_case = CreditWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
    buyer = make_buyer()
    run(user_repo.save(buyer))

    wallet = run(use_case.execute(
        actor_user_id=buyer.id,
        user_id=buyer.id,
        amount=Money(1000)
    ))

    assert wallet.balance == Money(1000)
    assert any(isinstance(event, WalletCredited) for event in fake_bus.published_events)


def test_credit_wallet_duplicate_reference_is_idempotent():
    wallet_repo = FakeWalletRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    use_case = CreditWallet(
        wallet_repository=wallet_repo,
        user_repository=user_repo,
        event_bus=fake_bus,
    )
    buyer = make_buyer()
    run(user_repo.save(buyer))

    first_wallet = run(use_case.execute(
        actor_user_id=buyer.id,
        user_id=buyer.id,
        amount=Money(1000),
        reference_id="topup-1",
    ))
    second_wallet = run(use_case.execute(
        actor_user_id=buyer.id,
        user_id=buyer.id,
        amount=Money(1000),
        reference_id="topup-1",
    ))

    assert first_wallet.balance == Money(1000)
    assert second_wallet.balance == Money(1000)
