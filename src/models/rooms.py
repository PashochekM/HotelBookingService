# ruff: noqa: F821

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class RoomsOrm(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_rooms_price_positive"),
        CheckConstraint("quantity > 0", name="ck_rooms_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[float]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities",
    )
