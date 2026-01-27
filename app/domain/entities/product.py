from dataclasses import dataclass
from app.domain.value_objects.money import Money

@dataclass
class Product:
      id: str
      tenant_id: str
      name: str
      price: Money
      stock: int