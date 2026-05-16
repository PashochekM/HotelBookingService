from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


async def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
):
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_booked"))
        .select_from(BookingsOrm)
        .filter(
            BookingsOrm.date_from <= date_to,
            BookingsOrm.date_to >= date_from,
        )
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")
    )
    rooms_left_table = (
        select(
            RoomsOrm.id.label("room_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
        )
        .select_from(RoomsOrm)
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte(name="rooms_left_table")
    )

    rooms_ids = select(RoomsOrm.id).select_from(RoomsOrm)
    if hotel_id is not None:
        rooms_ids = rooms_ids.filter_by(hotel_id=hotel_id)

    query = select(rooms_left_table.c.room_id).filter(
        rooms_left_table.c.rooms_left > 0,
        rooms_left_table.c.room_id.in_(rooms_ids),
    )
    ##print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
    return query
