from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class BuyerRegistered(DomainEvent):
    user_id: str
    email: str
    name: str
