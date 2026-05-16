"""init

Revision ID: 3cf8d936e4a7
Revises:
Create Date: 2026-03-22 14:42:43.000769

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3cf8d936e4a7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hotels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("hotels")
