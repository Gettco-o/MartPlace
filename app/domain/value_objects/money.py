from dataclasses import dataclass
from functools import total_ordering

@dataclass(frozen=True)
@total_ordering
class Money:
      amount: int # in kobo

      def add(self, other: "Money") -> "Money":
            return Money(self.amount + other.amount)
      
      def subtract(self, other: "Money") -> "Money":
            if other.amount > self.amount:
                  raise ValueError("Subtraction would result in negative amount")
            return Money(self.amount - other.amount)
      
      def multiply(self, factor: float) -> "Money":
            return Money(int(self.amount * factor))
      
      def __eq__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount == value.amount
      
      def __lt__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount < value.amount