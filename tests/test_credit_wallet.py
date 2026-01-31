from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from app.domain.value_objects.money import Money

def test_credit_wallet():
    # Arrange
    wallet_repo = FakeWalletRepository()
    use_case = CreditWallet(wallet_repository=wallet_repo)

    wallet = use_case.execute(
        tenant_id="tenant_1",
        user_id="user_1",
        amount=Money(1000)
    )

    assert wallet.balance == Money(1000)