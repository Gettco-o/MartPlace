from dataclasses import dataclass

@dataclass
class Tenant:
      id: str
      name: str
      is_active: bool = True