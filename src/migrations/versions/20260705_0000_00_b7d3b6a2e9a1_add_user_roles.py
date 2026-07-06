"""add user roles

Revision ID: b7d3b6a2e9a1
Revises: 633521f1cd7f
Create Date: 2026-07-05 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7d3b6a2e9a1"
down_revision: str | Sequence[str] | None = "633521f1cd7f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
