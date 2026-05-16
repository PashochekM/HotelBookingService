from fastapi import APIRouter, Body, HTTPException

from src.api.dependcencies import DBDep, UserIdDep
from src.repos.exceptions import RoomNotAvailableError
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
    _room = await db.rooms.get_one_or_none(id=book_data.room_id)
    if _room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    _new_booking = BookingAdd(
        user_id=user_id, price=_room.price, **book_data.model_dump()
    )
    try:
        result = await db.bookings.add_booking(_new_booking)
        await db.commit()
    except RoomNotAvailableError:
        raise HTTPException(
            status_code=409, detail="Room is not available for the selected dates"
        )
    return {"data": result}
