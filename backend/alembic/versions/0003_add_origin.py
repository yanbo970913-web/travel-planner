"""add origin column to itineraries

Revision ID: 0003_add_origin
Revises: 0002_pikmin_cache
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_add_origin"
down_revision: Union[str, None] = "0002_pikmin_cache"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "itineraries", sa.Column("origin", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("itineraries", "origin")
