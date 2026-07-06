from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class BookingsOrm(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("date_to > date_from", name="ck_bookings_dates"),
        CheckConstraint("price > 0", name="ck_bookings_price_positive"),
        CheckConstraint("status IN ('active', 'cancelled')", name="ck_bookings_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[float]
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active", nullable=False)

    @hybrid_property
    def total_cost(self) -> float:
        return self.price * (self.date_to - self.date_from).days
