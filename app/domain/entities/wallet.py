from dataclasses import dataclass
from app.domain.value_objects.money import Money

@dataclass
class Wallet:
      tenant_id: str
      user_id: str
      balance: Money

      def debit(self, amount: Money) -> None:
            self.balance = self.balance.subtract(amount)

      def credit(self, amount: Money) -> None:
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