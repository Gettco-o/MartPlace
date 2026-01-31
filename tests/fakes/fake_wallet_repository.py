# tests/fakes/fake_wallet_repository.py
from app.interfaces.repositories.wallet_repository import WalletRepository

class FakeWalletRepository(WalletRepository):

    def __init__(self):
        self.wallets = {}  # key: (tenant_id, user_id), value: wallet

    def get_wallet(self, tenant_id: str, user_id: str):
        return self.wallets.get((tenant_id, user_id))

    def save(self, wallet):
        key = (wallet.tenant_id, wallet.user_id)
        self.wallets[key] = wallet
