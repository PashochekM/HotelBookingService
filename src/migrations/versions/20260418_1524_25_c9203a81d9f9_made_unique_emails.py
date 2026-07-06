"""made unique emails

Revision ID: c9203a81d9f9
Revises: 10226314e88b
Create Date: 2026-04-18 15:24:25.829366

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9203a81d9f9"
down_revision: str | Sequence[str] | None = "10226314e88b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
