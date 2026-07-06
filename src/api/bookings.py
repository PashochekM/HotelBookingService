from fastapi import APIRouter, Body

from src.api.dependencies import AdminDep, BookingsServiceDep, CurrentUserDep
from src.schemas.bookings import Booking, BookingRequestAdd
from src.schemas.responses import DataResponse

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("/me", response_model=DataResponse[list[Booking]])
async def get_own_bookings(
    current_user: CurrentUserDep,
    bookings_service: BookingsServiceDep,
):
    result = await bookings_service.get_own_bookings(current_user.id)
    return {"data": result}


@router.get("", response_model=DataResponse[list[Booking]])
async def get_all_bookings(
    bookings_service: BookingsServiceDep,
    _admin: AdminDep,
):
    result = await bookings_service.get_all_bookings()
    return {"data": result}


@router.post("", response_model=DataResponse[Booking])
async def create_booking(
    current_user: CurrentUserDep,
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
    result = await bookings_service.create_booking(current_user.id, book_data)
    return {"data": result}


@router.patch("/{booking_id}/cancel", response_model=DataResponse[Booking])
async def cancel_booking(
    booking_id: int,
    current_user: CurrentUserDep,
    bookings_service: BookingsServiceDep,
):
    result = await bookings_service.cancel_booking(booking_id, current_user)
    return {"data": result}
