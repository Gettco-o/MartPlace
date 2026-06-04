from enum import Enum

class OrderStatus(str, Enum):
      CREATED = "created"
      PAID = "paid"
      PROCESSING = "processing"
      FULFILLED = "fulfilled"
      DELIVERED = "delivered"
      CANCELLED = "cancelled"
      FAILED = "failed"
      REFUNDED = "refunded"
