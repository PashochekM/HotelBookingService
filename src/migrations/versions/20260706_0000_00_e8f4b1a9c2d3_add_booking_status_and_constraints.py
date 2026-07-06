"""add booking status and constraints

Revision ID: e8f4b1a9c2d3
Revises: d0e6e4f8a2b9
Create Date: 2026-07-06 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e8f4b1a9c2d3"
down_revision: str | Sequence[str] | None = "d0e6e4f8a2b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
    )

    op.execute("UPDATE bookings SET date_to = date_from + INTERVAL '1 day' WHERE date_to <= date_from")
    op.execute("UPDATE bookings SET price = 1 WHERE price <= 0")
    op.execute("UPDATE rooms SET price = 1 WHERE price <= 0")
    op.execute("UPDATE rooms SET quantity = 1 WHERE quantity <= 0")
    op.execute(
        """
        DELETE FROM rooms_facilities newer
        USING rooms_facilities older
        WHERE newer.room_id = older.room_id
          AND newer.facility_id = older.facility_id
          AND newer.id > older.id
        """
    )

    op.create_check_constraint(
        "ck_bookings_status",
        "bookings",
        "status IN ('active', 'cancelled')",
    )
    op.create_check_constraint("ck_bookings_dates", "bookings", "date_to > date_from")
    op.create_check_constraint("ck_bookings_price_positive", "bookings", "price > 0")
    op.create_check_constraint("ck_rooms_price_positive", "rooms", "price > 0")
    op.create_check_constraint("ck_rooms_quantity_positive", "rooms", "quantity > 0")
    op.create_unique_constraint(
        "uq_rooms_facilities_room_id_facility_id",
        "rooms_facilities",
        ["room_id", "facility_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_rooms_facilities_room_id_facility_id", "rooms_facilities", type_="unique")
    op.drop_constraint("ck_rooms_quantity_positive", "rooms", type_="check")
    op.drop_constraint("ck_rooms_price_positive", "rooms", type_="check")
    op.drop_constraint("ck_bookings_price_positive", "bookings", type_="check")
    op.drop_constraint("ck_bookings_dates", "bookings", type_="check")
    op.drop_constraint("ck_bookings_status", "bookings", type_="check")
    op.drop_column("bookings", "status")
