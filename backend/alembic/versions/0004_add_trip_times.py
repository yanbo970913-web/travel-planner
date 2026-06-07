"""add start_date / departure_time / return_time to itineraries

Revision ID: 0004_add_trip_times
Revises: 0003_add_origin
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_add_trip_times"
down_revision: Union[str, None] = "0003_add_origin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "itineraries", sa.Column("start_date", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "itineraries", sa.Column("departure_time", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "itineraries", sa.Column("return_time", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("itineraries", "return_time")
    op.drop_column("itineraries", "departure_time")
    op.drop_column("itineraries", "start_date")
