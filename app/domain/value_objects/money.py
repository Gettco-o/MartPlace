from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
      amount: int # in kobo

      def add(self, other: "Money") -> "Money":
            return Money(self.amount + other.amount)
      
      def subtract(self, other: "Money") -> "Money":
            if other.amount > self.amount:
                  raise ValueError("Insufficient funds")
            return Money(self.amount - other.amount)
      def multiply(self, factor: float) -> "Money":
            return Money(int(self.amount * factor))