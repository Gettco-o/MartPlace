from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from app.domain.value_objects.money import Money


class TenantLedgerEntryType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


@dataclass(frozen=True)
class TenantLedgerEntry:
    id: str
    tenant_id: str
    amount: Money
    entry_type: TenantLedgerEntryType
    reference_id: str
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_credit(
        cls,
        tenant_id: str,
        amount: Money,
        reference_id: str,
    ) -> "TenantLedgerEntry":
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            amount=amount,
            entry_type=TenantLedgerEntryType.CREDIT,
            reference_id=reference_id,
        )

    @classmethod
    def create_debit(
        cls,
        tenant_id: str,
        amount: Money,
        reference_id: str,
    ) -> "TenantLedgerEntry":
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            amount=amount,
            entry_type=TenantLedgerEntryType.DEBIT,
            reference_id=reference_id,
        )
