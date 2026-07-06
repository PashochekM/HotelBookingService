"""add user roles

Revision ID: b7d3b6a2e9a1
Revises: 633521f1cd7f
Create Date: 2026-07-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7d3b6a2e9a1"
down_revision: Union[str, Sequence[str], None] = "633521f1cd7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
