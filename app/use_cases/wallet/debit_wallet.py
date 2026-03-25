from app.domain.exceptions import DomainError
from dataclasses import dataclass
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.value_objects.money import Money
import uuid


@dataclass
class DebitWallet:
    wallet_repository: WalletRepository
    tenant_repository: TenantRepository
    event_bus: EventBus

    def execute(
        self,
        tenant_id: str,
        user_id: str,
        amount: Money,
        reference_id: str | None = None,
    ):
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        wallet = self.wallet_repository.get_wallet(tenant_id, user_id)

        if wallet is None:
            raise DomainError("Wallet does not exist")

        reference_id = reference_id or f"wallet-debit:{uuid.uuid4()}"
        if self.wallet_repository.has_reference(tenant_id, user_id, reference_id):
            return self.wallet_repository.get_wallet(tenant_id, user_id)

        entry = wallet.debit(amount, reference_id=reference_id)
        self.wallet_repository.append_entry(entry)
        self.event_bus.publish(wallet.events)
        wallet.clear_events()

        return wallet
