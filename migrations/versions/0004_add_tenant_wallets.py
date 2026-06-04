"""add tenant wallets

Revision ID: 0004_add_tenant_wallets
Revises: 0003_make_wallet_platform_wide
Create Date: 2026-04-01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_add_tenant_wallets"
down_revision = "0003_make_wallet_platform_wide"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_ledger_entries",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.Enum("CREDIT", "DEBIT", name="tenantledgerentrytype", native_enum=False), nullable=False),
        sa.Column("reference_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "reference_id", name="uq_tenant_ledger_entries_reference"),
    )
    op.create_index(op.f("ix_tenant_ledger_entries_tenant_id"), "tenant_ledger_entries", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_tenant_ledger_entries_reference_id"), "tenant_ledger_entries", ["reference_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tenant_ledger_entries_reference_id"), table_name="tenant_ledger_entries")
    op.drop_index(op.f("ix_tenant_ledger_entries_tenant_id"), table_name="tenant_ledger_entries")
    op.drop_table("tenant_ledger_entries")
