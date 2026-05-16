from datetime import date

from src.schemas.bookings import BookingAdd


async def test_add_booking(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2021, month=1, day=1),
        date_to=date(year=2021, month=1, day=14),
        price=100,
    )
    real_data = await db.bookings.add_one(booking_data)
    await db.commit()

    get_data = await db.bookings.get_one_or_none(id=real_data.id)

    assert get_data is not None
    assert get_data == real_data
