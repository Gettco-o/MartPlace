from app.domain.entities.idempotency import IdempotencyRecord
from app.infrastructure.db.mappers import idempotency_to_entity, idempotency_to_model
from app.infrastructure.db.models import IdempotencyRecordModel
from app.interfaces.repositories.idempotency_repository import IdempotencyRepository


class SqlAlchemyIdempotencyRepository(IdempotencyRepository):
    def __init__(self, session) -> None:
        self.session = session

    async def get(self, key: str, operation: str) -> IdempotencyRecord | None:
        model = await self.session.get(
            IdempotencyRecordModel,
            {"key": key, "operation": operation},
        )
        if model is None:
            return None
        return idempotency_to_entity(model)

    async def save(self, record) -> None:
        model = await self.session.get(
            IdempotencyRecordModel,
            {"key": record.key, "operation": record.operation},
        )
        model = idempotency_to_model(record, model)
        self.session.add(model)
        await self.session.flush()
