"""make wallet platform wide

Revision ID: 0003_make_wallet_platform_wide
Revises: 0002_add_commerce_tables
Create Date: 2026-03-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_make_wallet_platform_wide"
down_revision = "0002_add_commerce_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_ledger_entries_reference", "ledger_entries", type_="unique")
    op.drop_constraint("ledger_entries_tenant_id_fkey", "ledger_entries", type_="foreignkey")
    op.drop_index("ix_ledger_entries_tenant_id", table_name="ledger_entries")
    op.drop_column("ledger_entries", "tenant_id")
    op.create_unique_constraint(
        "uq_ledger_entries_reference",
        "ledger_entries",
        ["user_id", "reference_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_ledger_entries_reference", "ledger_entries", type_="unique")
    op.add_column(
        "ledger_entries",
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_ledger_entries_tenant_id", "ledger_entries", ["tenant_id"], unique=False)
    op.create_foreign_key(
        "ledger_entries_tenant_id_fkey",
        "ledger_entries",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE ledger_entries
        SET tenant_id = (
            SELECT orders.tenant_id
            FROM orders
            WHERE orders.user_id = ledger_entries.user_id
            ORDER BY orders.created_at ASC
            LIMIT 1
        )
        """
    )
    op.alter_column("ledger_entries", "tenant_id", nullable=False)
    op.create_unique_constraint(
        "uq_ledger_entries_reference",
        "ledger_entries",
        ["tenant_id", "user_id", "reference_id"],
    )
