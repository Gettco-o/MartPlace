from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.ledger_entry import LedgerEntryType
from app.domain.entities.tenant_ledger_entry import TenantLedgerEntryType
from app.infrastructure.db.base import Base


class LedgerEntryModel(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "reference_id", name="uq_ledger_entries_reference"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType, native_enum=False),
        nullable=False,
    )
    reference_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TenantLedgerEntryModel(Base):
    __tablename__ = "tenant_ledger_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "reference_id", name="uq_tenant_ledger_entries_reference"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_type: Mapped[TenantLedgerEntryType] = mapped_column(
        Enum(TenantLedgerEntryType, native_enum=False),
        nullable=False,
    )
    reference_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
