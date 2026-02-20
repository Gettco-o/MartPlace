from app.domain.exceptions import DomainError
from dataclasses import dataclass
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.value_objects.money import Money

@dataclass
class DebitWallet:
      wallet_repository: WalletRepository
      tenant_repository: TenantRepository

      def execute(self, tenant_id: str, user_id: str, amount: Money):
            tenant = self.tenant_repository.get_by_id(tenant_id)
            if not tenant:
                  raise DomainError("Tenant not found")

            tenant.ensure_active()

            wallet = self.wallet_repository.get_wallet(tenant_id, user_id)

            if wallet is None:
                  raise DomainError("Wallet does not exist")
            
            wallet.debit(amount)
            self.wallet_repository.save(wallet)

            return wallet
