from datetime import date

import pytest

from src.exceptions import ObjectAlreadyExistsError
from src.schemas.bookings import BookingAdd
from src.schemas.facilities import FacilityAdd, RoomFacilityAdd


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


async def test_duplicate_room_facility_is_rejected(db):
    room_id = (await db.rooms.get_all())[0].id
    facility = await db.facilities.add_one(FacilityAdd(title="Duplicate relation test facility"))
    relation = RoomFacilityAdd(room_id=room_id, facility_id=facility.id)
    await db.rooms_facilities.add_bulk([relation])
    await db.commit()

    with pytest.raises(ObjectAlreadyExistsError):
        await db.rooms_facilities.add_bulk([relation])
        await db.commit()
