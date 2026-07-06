"""make booking price float

Revision ID: d0e6e4f8a2b9
Revises: b7d3b6a2e9a1
Create Date: 2026-07-05 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d0e6e4f8a2b9"
down_revision: Union[str, Sequence[str], None] = "b7d3b6a2e9a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "bookings",
        "price",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "bookings",
        "price",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
