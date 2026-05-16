from fastapi import APIRouter, Body

from src.api.dependcencies import BookingsServiceDep, UserIdDep
from src.schemas.bookings import BookingRequestAdd

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("/me")
async def get_own_bookings(
    user_id: UserIdDep,
    bookings_service: BookingsServiceDep,
):
    result = await bookings_service.get_own_bookings(user_id)
    return {"data": result}


@router.get("")
async def get_all_bookings(
    bookings_service: BookingsServiceDep,
):
    result = await bookings_service.get_all_bookings()
    return {"data": result}


@router.post("")
async def create_booking(
    user_id: UserIdDep,
    bookings_service: BookingsServiceDep,
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
    result = await bookings_service.create_booking(user_id, book_data)
    return {"data": result}
