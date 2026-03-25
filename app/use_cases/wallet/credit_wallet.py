from app.domain.entities.wallet import Wallet
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from dataclasses import dataclass
import uuid


@dataclass
class CreditWallet:
    wallet_repository: WalletRepository
    tenant_repository: TenantRepository
    event_bus: EventBus

    def execute(
        self,
        tenant_id: str,
        user_id: str,
        amount: Money,
        reference_id: str | None = None,
    ) -> Wallet:
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()

        wallet = self.wallet_repository.get_wallet(tenant_id, user_id)
        if wallet is None:
            wallet = Wallet(
                tenant_id=tenant_id,
                user_id=user_id,
            )

        reference_id = reference_id or f"wallet-credit:{uuid.uuid4()}"
        if self.wallet_repository.has_reference(tenant_id, user_id, reference_id):
            return self.wallet_repository.get_wallet(tenant_id, user_id)

        entry = wallet.credit(amount, reference_id=reference_id)
        self.wallet_repository.append_entry(entry)
        self.event_bus.publish(wallet.events)
        wallet.clear_events()

        return wallet
