from dataclasses import dataclass
from app.domain.value_objects.money import Money
from app.domain.exceptions import InsufficientFundsError, InvalidAmountError

@dataclass
class Wallet:
      tenant_id: str
      user_id: str
      balance: Money

      def debit(self, amount: Money) -> None:
            if amount <= Money(0):
                  raise InvalidAmountError("Amount must be positive")
            if self.balance < amount:
                  raise InsufficientFundsError("Insufficient funds")
            self.balance = self.balance.subtract(amount)

      def credit(self, amount: Money) -> None:
            if amount <= Money(0):
                  raise InvalidAmountError("Amount must be positive")
            self.balance = self.balance.add(amount)

""" 
@dataclass
class LedgerEntry:
      id: str
      tenant_id: str
      user_id: str
      amount: Money
      entry_type: str  # 'debit' or 'credit'
      reference_id: str  
      timestamp: str

 """