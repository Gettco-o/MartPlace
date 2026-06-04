from dataclasses import dataclass
from functools import total_ordering

@dataclass(frozen=True)
@total_ordering
class Money:
      amount: int # in kobo

      def add(self, other: "Money") -> "Money":
            return Money(self.amount + other.amount)
      
      def subtract(self, other: "Money") -> "Money":
            return Money(self.amount - other.amount)
      
      def multiply(self, factor: int) -> "Money":
            """Multiply money by an integer factor (e.g. quantity).

            Note: Money.amount is an integer unit (e.g. cents/kobo). Multiplying
            by non-integer factors is not supported here - pass an int.
            """
            return Money(self.amount * int(factor))
      
      def __eq__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount == value.amount
      
      def __lt__(self, value):
            if not isinstance(value, Money):
                  return NotImplemented
            return self.amount < value.amount