from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class WalletCredited(DomainEvent):
    tenant_id: str
    user_id: str
    amount: int | float
    balance: int | float
