from sqlalchemy import select

from app.domain.entities.tenant_ledger_entry import TenantLedgerEntry
from app.domain.entities.tenant_wallet import TenantWallet
from app.infrastructure.db.mappers import (
    tenant_ledger_entry_to_entity,
    tenant_ledger_entry_to_model,
)
from app.infrastructure.db.models import TenantLedgerEntryModel
from app.interfaces.repositories.tenant_wallet_repository import TenantWalletRepository


class SqlAlchemyTenantWalletRepository(TenantWalletRepository):
    def __init__(self, session) -> None:
        self.session = session

    async def get_wallet(self, tenant_id: str) -> TenantWallet | None:
        stmt = (
            select(TenantLedgerEntryModel)
            .where(TenantLedgerEntryModel.tenant_id == tenant_id)
            .order_by(TenantLedgerEntryModel.created_at.asc(), TenantLedgerEntryModel.id.asc())
        )
        result = await self.session.scalars(stmt)
        entries = [tenant_ledger_entry_to_entity(model) for model in result.all()]
        if not entries:
            return None
        return TenantWallet(tenant_id=tenant_id, entries=entries)

    async def append_entry(self, entry: TenantLedgerEntry) -> None:
        model = await self.session.get(TenantLedgerEntryModel, entry.id)
        model = tenant_ledger_entry_to_model(entry, model)
        self.session.add(model)
        await self.session.flush()

    async def has_reference(self, tenant_id: str, reference_id: str) -> bool:
        stmt = select(TenantLedgerEntryModel.id).where(
            TenantLedgerEntryModel.tenant_id == tenant_id,
            TenantLedgerEntryModel.reference_id == reference_id,
        )
        result = await self.session.scalar(stmt)
        return result is not None
