from app.interfaces.repositories.wallet_repository import WalletRepository
from app.domain.entities.wallet import Wallet

class FakeWalletRepository(WalletRepository):

    def __init__(self):
        self.wallets: dict[tuple[str,str], Wallet] = {}

    def get_wallet(self, tenant_id: str, user_id: str)-> Wallet:
        return self.wallets.get((tenant_id, user_id))

    def save(self, wallet):
        key = (wallet.tenant_id, wallet.user_id)
        self.wallets[key] = wallet
