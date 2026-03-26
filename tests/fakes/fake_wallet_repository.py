from app.domain.entities.ledger_entry import LedgerEntry
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.entities.wallet import Wallet


class FakeWalletRepository(WalletRepository):

    def __init__(self):
        self.entries: dict[tuple[str, str], list[LedgerEntry]] = {}

    async def get_wallet(self, tenant_id: str, user_id: str) -> Wallet | None:
        key = (tenant_id, user_id)
        if key not in self.entries:
            return None

        return Wallet(
            tenant_id=tenant_id,
            user_id=user_id,
            entries=list(self.entries[key]),
        )

    async def append_entry(self, entry: LedgerEntry) -> None:
        key = (entry.tenant_id, entry.user_id)
        self.entries.setdefault(key, []).append(entry)

    async def has_reference(self, tenant_id: str, user_id: str, reference_id: str) -> bool:
        key = (tenant_id, user_id)
        return any(
            entry.reference_id == reference_id
            for entry in self.entries.get(key, [])
        )
