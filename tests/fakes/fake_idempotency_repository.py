from app.interfaces.repositories.idempotency_repository import IdempotencyRepository
from app.domain.entities.idempotency import IdempotencyRecord


class FakeIdempotencyRepository(IdempotencyRepository):

    def __init__(self):
        self.records: dict[tuple[str, str], IdempotencyRecord] = {}

    def get(self, key: str, operation: str) -> IdempotencyRecord:
        return self.records.get((key, operation))

    def save(self, record):
        self.records[(record.key, record.operation)] = record