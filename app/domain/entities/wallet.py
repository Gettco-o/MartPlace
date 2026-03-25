from dataclasses import dataclass
from datetime import datetime
from app.domain.entities.entity_with_events import EntityWithEvents
from app.domain.events.wallet_credited import WalletCredited
from app.domain.events.wallet_debited import WalletDebited
from app.domain.value_objects.money import Money
from app.domain.exceptions import InsufficientFundsError, InvalidAmountError

@dataclass
class Wallet(EntityWithEvents):
      tenant_id: str
      user_id: str
      balance: Money

      def debit(self, amount: Money) -> None:
            if amount <= Money(0):
                  raise InvalidAmountError("Amount must be positive")
            if self.balance < amount:
                  raise InsufficientFundsError("Insufficient funds")
            self.balance = self.balance.subtract(amount)
            self.record_event(
                  WalletDebited(
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        amount=amount.amount,
                        balance=self.balance.amount,
                        occurred_at=datetime.now(),
                  )
            )

      def credit(self, amount: Money) -> None:
            if amount <= Money(0):
                  raise InvalidAmountError("Amount must be positive")
            self.balance = self.balance.add(amount)
            self.record_event(
                  WalletCredited(
                        tenant_id=self.tenant_id,
                        user_id=self.user_id,
                        amount=amount.amount,
                        balance=self.balance.amount,
                        occurred_at=datetime.now(),
                  )
            )

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
