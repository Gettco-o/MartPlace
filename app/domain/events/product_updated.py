from dataclasses import dataclass

from app.domain.events.base import DomainEvent


@dataclass
class ProductUpdated(DomainEvent):
    product_id: str
    tenant_id: str
    name: str
    price_amount: int | float
    stock: int
