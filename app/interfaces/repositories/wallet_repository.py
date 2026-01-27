from abc import ABC, abstractmethod
from app.domain.entities.wallet import Wallet

class WalletRepository(ABC):
      @abstractmethod
      def get_wallet(self, tenant_id: str, user_id: str) -> Wallet | None:
            pass

      @abstractmethod
      def save(self, wallet: Wallet) -> None:
            pass