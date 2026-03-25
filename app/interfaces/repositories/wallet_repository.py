from abc import ABC, abstractmethod

from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.entities.wallet import Wallet


class WalletRepository(ABC):
    @abstractmethod
    def get_wallet(self, tenant_id: str, user_id: str) -> Wallet | None:
        pass

    @abstractmethod
    def append_entry(self, entry: LedgerEntry) -> None:
        pass

    @abstractmethod
    def has_reference(self, tenant_id: str, user_id: str, reference_id: str) -> bool:
        pass
