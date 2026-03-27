from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.entity_with_events import EntityWithEvents
from app.domain.entities.ledger_entry import LedgerEntry, LedgerEntryType
from app.domain.events.wallet_credited import WalletCredited
from app.domain.events.wallet_debited import WalletDebited
from app.domain.exceptions import InsufficientFundsError, InvalidAmountError
from app.domain.value_objects.money import Money


@dataclass
class Wallet(EntityWithEvents):
    user_id: str
    entries: list[LedgerEntry] = field(default_factory=list)

    @property
    def balance(self) -> Money:
        running_total = 0

        for entry in self.entries:
            if entry.entry_type == LedgerEntryType.CREDIT:
                running_total += entry.amount.amount
            else:
                running_total -= entry.amount.amount

        return Money(running_total)

    def has_reference(self, reference_id: str) -> bool:
        return any(entry.reference_id == reference_id for entry in self.entries)

    def debit(self, amount: Money, reference_id: str) -> LedgerEntry:
        if amount <= Money(0):
            raise InvalidAmountError("Amount must be positive")
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient funds")

        entry = LedgerEntry.create_debit(
            user_id=self.user_id,
            amount=amount,
            reference_id=reference_id,
        )
        self.entries.append(entry)
        self.record_event(
            WalletDebited(
                user_id=self.user_id,
                amount=amount.amount,
                balance=self.balance.amount,
                occurred_at=datetime.now(),
            )
        )
        return entry

    def credit(self, amount: Money, reference_id: str) -> LedgerEntry:
        if amount <= Money(0):
            raise InvalidAmountError("Amount must be positive")

        entry = LedgerEntry.create_credit(
            user_id=self.user_id,
            amount=amount,
            reference_id=reference_id,
        )
        self.entries.append(entry)
        self.record_event(
            WalletCredited(
                user_id=self.user_id,
                amount=amount.amount,
                balance=self.balance.amount,
                occurred_at=datetime.now(),
            )
        )
        return entry
