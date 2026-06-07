"""pikmin_cache table

Revision ID: 0002_pikmin_cache
Revises: 0001_initial
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_pikmin_cache"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pikmin_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location", "date", name="uq_pikmin_location_date"),
    )
    op.create_index(
        "ix_pikmin_cache_location", "pikmin_cache", ["location"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_pikmin_cache_location", table_name="pikmin_cache")
    op.drop_table("pikmin_cache")
