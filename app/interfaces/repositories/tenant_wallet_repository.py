from abc import ABC, abstractmethod

from app.domain.entities.tenant_wallet import TenantWallet
from app.domain.entities.tenant_ledger_entry import TenantLedgerEntry


class TenantWalletRepository(ABC):
    @abstractmethod
    async def get_wallet(self, tenant_id: str) -> TenantWallet | None:
        pass

    @abstractmethod
    async def append_entry(self, entry: TenantLedgerEntry) -> None:
        pass

    @abstractmethod
    async def has_reference(self, tenant_id: str, reference_id: str) -> bool:
        pass
