"""add users

Revision ID: 10226314e88b
Revises: 47963f0db1d1
Create Date: 2026-04-18 14:59:55.532767

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "10226314e88b"
down_revision: Union[str, Sequence[str], None] = "47963f0db1d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("hashed_password", sa.String(length=200), nullable=False)
    )
    op.drop_column("users", "password")



def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password", sa.VARCHAR(length=200), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("users", "hashed_password")
