from dataclasses import dataclass

@dataclass
class IdempotencyRecord:
      key: str
      operation: str
      result_id: str