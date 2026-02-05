from enum import Enum

class IdempotentOperation(str, Enum):
      CREATE_ORDER = "create_order"