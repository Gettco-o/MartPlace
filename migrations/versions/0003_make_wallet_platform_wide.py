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
    with op.batch_alter_table("ledger_entries", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_ledger_entries_reference", type_="unique")
        batch_op.drop_index("ix_ledger_entries_tenant_id")
        batch_op.drop_column("tenant_id")
        batch_op.create_unique_constraint(
            "uq_ledger_entries_reference",
            ["user_id", "reference_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("ledger_entries", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_ledger_entries_reference", type_="unique")
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=64), nullable=True))

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

    with op.batch_alter_table("ledger_entries", recreate="always") as batch_op:
        batch_op.alter_column("tenant_id", existing_type=sa.String(length=64), nullable=False)
        batch_op.create_index("ix_ledger_entries_tenant_id", ["tenant_id"], unique=False)
        batch_op.create_foreign_key(
            None,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_unique_constraint(
            "uq_ledger_entries_reference",
            ["tenant_id", "user_id", "reference_id"],
        )
