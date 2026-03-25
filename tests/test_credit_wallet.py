from app.domain.events.wallet_credited import WalletCredited
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from app.domain.value_objects.money import Money

def test_credit_wallet():
    # Arrange
    wallet_repo = FakeWalletRepository()
    tenant_repo = FakeTenantRepository()
    fake_bus = FakeEventBus()
    use_case = CreditWallet(wallet_repository=wallet_repo, tenant_repository=tenant_repo, event_bus=fake_bus)

    create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

    tenant = create_tenant_use_case.execute(name="Shop A")

    wallet = use_case.execute(
        tenant_id=tenant.id,
        user_id="user_1",
        amount=Money(1000)
    )

    assert wallet.balance == Money(1000)
    assert any(isinstance(event, WalletCredited) for event in fake_bus.published_events)
