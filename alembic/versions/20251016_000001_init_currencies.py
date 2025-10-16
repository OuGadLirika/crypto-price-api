"""init currencies table

Revision ID: 20251016_000001
Revises: 
Create Date: 2025-10-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251016_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "currencies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("currency", sa.String(length=32), nullable=False),
        sa.Column("date_", sa.DateTime(timezone=False), nullable=False),
        sa.Column("price", sa.Numeric(precision=24, scale=10), nullable=False),
    )
    op.create_index("ix_currencies_currency", "currencies", ["currency"], unique=False)
    op.create_index("ix_currencies_date_", "currencies", ["date_"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_currencies_currency", table_name="currencies")
    op.drop_index("ix_currencies_date_", table_name="currencies")
    op.drop_table("currencies")
