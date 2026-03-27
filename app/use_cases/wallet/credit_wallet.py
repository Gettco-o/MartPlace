from app.domain.entities.wallet import Wallet
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.user_repository import UserRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.auth import ensure_active_buyer
from dataclasses import dataclass
import uuid


@dataclass
class CreditWallet:
    wallet_repository: WalletRepository
    user_repository: UserRepository
    event_bus: EventBus

    async def execute(
        self,
        actor_user_id: str,
        user_id: str,
        amount: Money,
        reference_id: str | None = None,
    ) -> Wallet:
        await ensure_active_buyer(self.user_repository, actor_user_id, user_id)

        wallet = await self.wallet_repository.get_wallet(user_id)
        if wallet is None:
            wallet = Wallet(
                user_id=user_id,
            )

        reference_id = reference_id or f"wallet-credit:{uuid.uuid4()}"
        if await self.wallet_repository.has_reference(user_id, reference_id):
            return await self.wallet_repository.get_wallet(user_id)

        entry = wallet.credit(amount, reference_id=reference_id)
        await self.wallet_repository.append_entry(entry)
        self.event_bus.publish(wallet.events)
        wallet.clear_events()

        return wallet
