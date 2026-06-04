from app.domain.entities.tenant_ledger_entry import TenantLedgerEntry
from app.domain.entities.tenant_wallet import TenantWallet
from app.interfaces.repositories.tenant_wallet_repository import TenantWalletRepository


class FakeTenantWalletRepository(TenantWalletRepository):
    def __init__(self):
        self.entries: dict[str, list[TenantLedgerEntry]] = {}

    async def get_wallet(self, tenant_id: str) -> TenantWallet | None:
        if tenant_id not in self.entries:
            return None

        return TenantWallet(
            tenant_id=tenant_id,
            entries=list(self.entries[tenant_id]),
        )

    async def append_entry(self, entry: TenantLedgerEntry) -> None:
        self.entries.setdefault(entry.tenant_id, []).append(entry)

    async def has_reference(self, tenant_id: str, reference_id: str) -> bool:
        return any(
            entry.reference_id == reference_id
            for entry in self.entries.get(tenant_id, [])
        )
