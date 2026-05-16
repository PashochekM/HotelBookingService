from fastapi import APIRouter, Body

from src.api.dependcencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAdd, BookingRequestAdd

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("/me")
async def get_own_bookings(
    user_id: UserIdDep,
    db: DBDep,
):
    result = await db.bookings.get_filtered(user_id=user_id)
    return {"data": result}


@router.get("")
async def get_all_bookings(
    db: DBDep,
):
    result = await db.bookings.get_all()
    return {"data": result}


@router.post("")
async def create_booking(
    user_id: UserIdDep,
    db: DBDep,
    book_data: BookingRequestAdd = Body(
        openapi_examples={
            "short_stay": {
                "summary": "Короткое бронирование",
                "description": "Бронирование комнаты на 2 ночи",
                "value": {
                    "room_id": 1,
                    "date_from": "2026-05-10",
                    "date_to": "2026-05-12",
                },
            },
            "vacation": {
                "summary": "Отпуск",
                "description": "Бронирование комнаты на неделю",
                "value": {
                    "room_id": 3,
                    "date_from": "2026-07-01",
                    "date_to": "2026-07-08",
                },
            },
        }
    ),
):
    _room = await db.rooms.get_one(id=book_data.room_id)

    _new_booking = BookingAdd(user_id=user_id, price=_room.price, **book_data.model_dump())
    result = await db.bookings.add_booking(_new_booking)
    await db.commit()
    return {"data": result}
