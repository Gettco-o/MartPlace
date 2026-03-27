from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class WalletDebited(DomainEvent):
    user_id: str
    amount: int | float
    balance: int | float
