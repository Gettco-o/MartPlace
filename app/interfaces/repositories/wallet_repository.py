from abc import ABC, abstractmethod

from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.entities.wallet import Wallet


class WalletRepository(ABC):
    @abstractmethod
    async def get_wallet(self, user_id: str) -> Wallet | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Wallet]:
        pass

    @abstractmethod
    async def append_entry(self, entry: LedgerEntry) -> None:
        pass

    @abstractmethod
    async def has_reference(self, user_id: str, reference_id: str) -> bool:
        pass
