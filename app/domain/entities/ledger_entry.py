from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from app.domain.value_objects.money import Money


class LedgerEntryType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


@dataclass(frozen=True)
class LedgerEntry:
    id: str
    tenant_id: str
    user_id: str
    amount: Money
    entry_type: LedgerEntryType
    reference_id: str
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_credit(
        cls,
        tenant_id: str,
        user_id: str,
        amount: Money,
        reference_id: str,
    ) -> "LedgerEntry":
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            amount=amount,
            entry_type=LedgerEntryType.CREDIT,
            reference_id=reference_id,
        )

    @classmethod
    def create_debit(
        cls,
        tenant_id: str,
        user_id: str,
        amount: Money,
        reference_id: str,
    ) -> "LedgerEntry":
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            amount=amount,
            entry_type=LedgerEntryType.DEBIT,
            reference_id=reference_id,
        )
