from dataclasses import dataclass
from typing import Any

@dataclass
class IdempotencyRecord:
      key: str
      operation: str
      result_id: Any
