from app.domain.entities.ledger_entry import LedgerEntry
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.entities.wallet import Wallet


class FakeWalletRepository(WalletRepository):

    def __init__(self):
        self.entries: dict[str, list[LedgerEntry]] = {}

    async def get_wallet(self, user_id: str) -> Wallet | None:
        if user_id not in self.entries:
            return None

        return Wallet(
            user_id=user_id,
            entries=list(self.entries[user_id]),
        )

    async def append_entry(self, entry: LedgerEntry) -> None:
        self.entries.setdefault(entry.user_id, []).append(entry)

    async def has_reference(self, user_id: str, reference_id: str) -> bool:
        return any(
            entry.reference_id == reference_id
            for entry in self.entries.get(user_id, [])
        )
