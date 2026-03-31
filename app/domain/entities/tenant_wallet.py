from dataclasses import dataclass, field

from app.domain.entities.tenant_ledger_entry import TenantLedgerEntry, TenantLedgerEntryType
from app.domain.exceptions import InsufficientFundsError, InvalidAmountError
from app.domain.value_objects.money import Money


@dataclass
class TenantWallet:
    tenant_id: str
    entries: list[TenantLedgerEntry] = field(default_factory=list)

    @property
    def balance(self) -> Money:
        running_total = 0

        for entry in self.entries:
            if entry.entry_type == TenantLedgerEntryType.CREDIT:
                running_total += entry.amount.amount
            else:
                running_total -= entry.amount.amount

        return Money(running_total)

    def credit(self, amount: Money, reference_id: str) -> TenantLedgerEntry:
        if amount <= Money(0):
            raise InvalidAmountError("Amount must be positive")

        entry = TenantLedgerEntry.create_credit(
            tenant_id=self.tenant_id,
            amount=amount,
            reference_id=reference_id,
        )
        self.entries.append(entry)
        return entry

    def debit(self, amount: Money, reference_id: str) -> TenantLedgerEntry:
        if amount <= Money(0):
            raise InvalidAmountError("Amount must be positive")
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient funds")

        entry = TenantLedgerEntry.create_debit(
            tenant_id=self.tenant_id,
            amount=amount,
            reference_id=reference_id,
        )
        self.entries.append(entry)
        return entry
