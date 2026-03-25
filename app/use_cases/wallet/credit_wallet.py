from app.domain.entities.wallet import Wallet
from app.domain.exceptions import DomainError
from app.domain.value_objects.money import Money
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from dataclasses import dataclass

@dataclass
class CreditWallet:
      wallet_repository: WalletRepository
      tenant_repository: TenantRepository
      event_bus: EventBus

      def execute(self, tenant_id: str, user_id: str, amount: Money) -> Wallet:
            tenant = self.tenant_repository.get_by_id(tenant_id)
            if not tenant:
                  raise DomainError("Tenant not found")

            tenant.ensure_active()

            wallet = self.wallet_repository.get_wallet(tenant_id, user_id)

            if wallet is None:
                  wallet = Wallet(
                        tenant_id=tenant_id,
                        user_id=user_id,
                        balance=Money(0)
                  )
            
            wallet.credit(amount)
            self.wallet_repository.save(wallet)
            self.event_bus.publish(wallet.events)
            wallet.clear_events()

            return wallet
