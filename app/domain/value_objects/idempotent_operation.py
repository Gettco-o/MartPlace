from enum import Enum

class IdempotentOperation(str, Enum):
      CREATE_ORDER = "create_order"
      REFUND_ORDER = "refund_order"