from dataclasses import dataclass

from app.domain.entities.tenant_wallet import TenantWallet
from app.domain.entities.wallet import Wallet


@dataclass
class WalletAmountRequest:
    amount: int
    reference_id: str | None = None


@dataclass
class WalletEntrySchema:
    id: str
    amount: int
    entry_type: str
    reference_id: str
    created_at: str


@dataclass
class WalletSchema:
    user_id: str
    balance: int
    entries: list[WalletEntrySchema]

    @classmethod
    def from_entity(cls, wallet: Wallet) -> "WalletSchema":
        return cls(
            user_id=wallet.user_id,
            balance=wallet.balance.amount,
            entries=[
                WalletEntrySchema(
                    id=entry.id,
                    amount=entry.amount.amount,
                    entry_type=entry.entry_type.value,
                    reference_id=entry.reference_id,
                    created_at=entry.created_at.isoformat(),
                )
                for entry in wallet.entries
            ],
        )


@dataclass
class WalletResponse:
    success: bool
    wallet: WalletSchema


@dataclass
class WalletsResponse:
    success: bool
    wallets: list[WalletSchema]


@dataclass
class TenantWalletEntrySchema:
    id: str
    amount: int
    entry_type: str
    reference_id: str
    created_at: str


@dataclass
class TenantWalletSchema:
    tenant_id: str
    balance: int
    entries: list[TenantWalletEntrySchema]

    @classmethod
    def from_entity(cls, wallet: TenantWallet) -> "TenantWalletSchema":
        return cls(
            tenant_id=wallet.tenant_id,
            balance=wallet.balance.amount,
            entries=[
                TenantWalletEntrySchema(
                    id=entry.id,
                    amount=entry.amount.amount,
                    entry_type=entry.entry_type.value,
                    reference_id=entry.reference_id,
                    created_at=entry.created_at.isoformat(),
                )
                for entry in wallet.entries
            ],
        )


@dataclass
class TenantWalletResponse:
    success: bool
    wallet: TenantWalletSchema
