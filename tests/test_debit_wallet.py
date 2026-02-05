import pytest
from app.domain.value_objects.money import Money
from app.use_cases.wallet.credit_wallet import CreditWallet
from app.use_cases.wallet.debit_wallet import DebitWallet
from app.domain.exceptions import InsufficientFundsError
from app.domain.exceptions import InvalidAmountError
from tests.fakes.fake_wallet_repository import FakeWalletRepository

def test_debit_wallet_success():
      repo = FakeWalletRepository()
      credit_use_case = CreditWallet(wallet_repository=repo)
      debit_use_case = DebitWallet(wallet_repository=repo)

      credit_use_case.execute("tenant_1", "user_1", Money(100))
      wallet = debit_use_case.execute("tenant_1", "user_1", Money(40))

      assert wallet.balance == Money(60)

def test_debit_wallet_insufficient_funds():
      repo = FakeWalletRepository()
      credit_use_case = CreditWallet(wallet_repository=repo)
      debit_use_case = DebitWallet(wallet_repository=repo)

      credit_use_case.execute("tenant_1", "user_1", Money(10))

      with pytest.raises(InsufficientFundsError):
            debit_use_case.execute("tenant_1", "user_1", Money(20))

def test_debit_wallet_invalid_amount():
      repo = FakeWalletRepository()
      credit_use_case = CreditWallet(repo)
      debit_use_case = DebitWallet(repo)

      credit_use_case.execute("tenant_1", "user_1", Money(100))

      with pytest.raises(InvalidAmountError):
            debit_use_case.execute("tenant_1", "user_1", Money(-5))
