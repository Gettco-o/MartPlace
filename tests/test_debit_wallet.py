import asyncio
import pytest
from app.domain.events.wallet_debited import WalletDebited
from app.domain.value_objects.money import Money
from app.use_cases.wallet.credit_wallet import CreditWallet
from app.use_cases.wallet.debit_wallet import DebitWallet
from app.domain.exceptions import InsufficientFundsError
from app.domain.exceptions import InvalidAmountError
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer

run = asyncio.run

def test_debit_wallet_success():
      wallet_repo = FakeWalletRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      buyer = make_buyer()
      run(user_repo.save(buyer))

      run(credit_use_case.execute(buyer.id, buyer.id, Money(100)))
      wallet = run(debit_use_case.execute(buyer.id, buyer.id, Money(40)))

      assert wallet.balance == Money(60)
      assert any(isinstance(event, WalletDebited) for event in fake_bus.published_events)

def test_debit_wallet_insufficient_funds():
      wallet_repo = FakeWalletRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      buyer = make_buyer()
      run(user_repo.save(buyer))

      run(credit_use_case.execute(buyer.id, buyer.id, Money(10)))

      with pytest.raises(InsufficientFundsError):
            run(debit_use_case.execute(buyer.id, buyer.id, Money(20)))

def test_debit_wallet_invalid_amount():
      wallet_repo = FakeWalletRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      buyer = make_buyer()
      run(user_repo.save(buyer))

      run(credit_use_case.execute(buyer.id, buyer.id, Money(100)))

      with pytest.raises(InvalidAmountError):
            run(debit_use_case.execute(buyer.id, buyer.id, Money(-5)))


def test_debit_wallet_duplicate_reference_is_idempotent():
      wallet_repo = FakeWalletRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, user_repository=user_repo, event_bus=fake_bus)
      buyer = make_buyer()
      run(user_repo.save(buyer))

      run(credit_use_case.execute(buyer.id, buyer.id, Money(100)))
      first_wallet = run(debit_use_case.execute(buyer.id, buyer.id, Money(40), reference_id="debit-1"))
      second_wallet = run(debit_use_case.execute(buyer.id, buyer.id, Money(40), reference_id="debit-1"))

      assert first_wallet.balance == Money(60)
      assert second_wallet.balance == Money(60)
