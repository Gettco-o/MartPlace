import pytest
from app.domain.events.wallet_debited import WalletDebited
from app.domain.value_objects.money import Money
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from app.use_cases.wallet.debit_wallet import DebitWallet
from app.domain.exceptions import InsufficientFundsError
from app.domain.exceptions import InvalidAmountError
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.helpers import make_buyer

def test_debit_wallet_success():
      wallet_repo = FakeWalletRepository()
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

      tenant = create_tenant_use_case.execute(name="Shop A")
      buyer = make_buyer()
      user_repo.save(buyer)

      credit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(100))
      wallet = debit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(40))

      assert wallet.balance == Money(60)
      assert any(isinstance(event, WalletDebited) for event in fake_bus.published_events)

def test_debit_wallet_insufficient_funds():
      wallet_repo = FakeWalletRepository()
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

      tenant = create_tenant_use_case.execute(name="Shop A")
      buyer = make_buyer()
      user_repo.save(buyer)

      credit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(10))

      with pytest.raises(InsufficientFundsError):
            debit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(20))

def test_debit_wallet_invalid_amount():
      wallet_repo = FakeWalletRepository()
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()
      credit_use_case = CreditWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)
      debit_use_case = DebitWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, user_repository=user_repo, event_bus=fake_bus)

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

      tenant = create_tenant_use_case.execute(name="Shop A")
      buyer = make_buyer()
      user_repo.save(buyer)

      credit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(100))

      with pytest.raises(InvalidAmountError):
            debit_use_case.execute(buyer.id, tenant.id, buyer.id, Money(-5))
