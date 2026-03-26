from app.domain.exceptions import DomainError
from dataclasses import dataclass
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_active_buyer
from app.domain.value_objects.money import Money
import uuid


@dataclass
class DebitWallet:
    wallet_repository: WalletRepository
    tenant_repository: TenantRepository
    user_repository: UserRepository
    event_bus: EventBus

    async def execute(
        self,
        actor_user_id: str,
        tenant_id: str,
        user_id: str,
        amount: Money,
        reference_id: str | None = None,
    ):
        tenant = await self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_active_buyer(self.user_repository, actor_user_id, user_id)

        wallet = await self.wallet_repository.get_wallet(tenant_id, user_id)

        if wallet is None:
            raise DomainError("Wallet does not exist")

        reference_id = reference_id or f"wallet-debit:{uuid.uuid4()}"
        if await self.wallet_repository.has_reference(tenant_id, user_id, reference_id):
            return await self.wallet_repository.get_wallet(tenant_id, user_id)

        entry = wallet.debit(amount, reference_id=reference_id)
        await self.wallet_repository.append_entry(entry)
        self.event_bus.publish(wallet.events)
        wallet.clear_events()

        return wallet
