from dataclasses import dataclass
from functools import total_ordering
from decimal import Decimal

@dataclass(frozen=True)
@total_ordering
class Money:
      amount: int # in kobo

      def add(self, other: "Money") -> "Money":
            return Money(self.amount + other.amount)
      
      def subtract(self, other: "Money") -> "Money":
            return Money(self.amount - other.amount)
      
      def multiply(self, factor: Decimal) -> "Money":
            return Money(int(self.amount * factor))
      
      def __eq__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount == value.amount
      
      def __lt__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount < value.amount