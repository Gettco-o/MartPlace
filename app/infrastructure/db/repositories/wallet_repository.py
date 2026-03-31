from sqlalchemy import select

from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.entities.wallet import Wallet
from app.infrastructure.db.mappers import ledger_entry_to_entity, ledger_entry_to_model
from app.infrastructure.db.models import LedgerEntryModel
from app.interfaces.repositories.wallet_repository import WalletRepository


class SqlAlchemyWalletRepository(WalletRepository):
    def __init__(self, session) -> None:
        self.session = session

    async def get_wallet(self, user_id: str) -> Wallet | None:
        stmt = (
            select(LedgerEntryModel)
            .where(
                LedgerEntryModel.user_id == user_id,
            )
            .order_by(LedgerEntryModel.created_at.asc(), LedgerEntryModel.id.asc())
        )
        result = await self.session.scalars(stmt)
        entries = [ledger_entry_to_entity(model) for model in result.all()]
        if not entries:
            return None
        return Wallet(user_id=user_id, entries=entries)

    async def list_all(self) -> list[Wallet]:
        stmt = (
            select(LedgerEntryModel)
            .order_by(
                LedgerEntryModel.user_id.asc(),
                LedgerEntryModel.created_at.asc(),
                LedgerEntryModel.id.asc(),
            )
        )
        result = await self.session.scalars(stmt)
        wallets: dict[str, list[LedgerEntry]] = {}
        for model in result.all():
            entry = ledger_entry_to_entity(model)
            wallets.setdefault(entry.user_id, []).append(entry)
        return [Wallet(user_id=user_id, entries=entries) for user_id, entries in wallets.items()]

    async def append_entry(self, entry: LedgerEntry) -> None:
        model = await self.session.get(LedgerEntryModel, entry.id)
        model = ledger_entry_to_model(entry, model)
        self.session.add(model)
        await self.session.flush()

    async def has_reference(self, user_id: str, reference_id: str) -> bool:
        stmt = select(LedgerEntryModel.id).where(
            LedgerEntryModel.user_id == user_id,
            LedgerEntryModel.reference_id == reference_id,
        )
        result = await self.session.scalar(stmt)
        return result is not None
