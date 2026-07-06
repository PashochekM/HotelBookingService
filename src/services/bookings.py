import logging

from src.exceptions import BookingAlreadyCancelledError, ObjectNotFoundError
from src.schemas.bookings import BookingAdd, BookingRequestAdd
from src.schemas.users import User
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class BookingsService(BaseService):
    async def get_own_bookings(self, user_id: int):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def get_all_bookings(self):
        return await self.db.bookings.get_all()

    async def create_booking(self, user_id: int, book_data: BookingRequestAdd):
        room = await self.db.rooms.get_one(id=book_data.room_id)
        booking_to_add = BookingAdd(user_id=user_id, price=room.price, **book_data.model_dump())
        result = await self.db.bookings.add_booking(booking_to_add)
        await self.db.commit()
        logger.info(
            "booking_created booking_id=%s user_id=%s room_id=%s date_from=%s date_to=%s",
            result.id,
            user_id,
            book_data.room_id,
            book_data.date_from,
            book_data.date_to,
        )
        return result

    async def cancel_booking(self, booking_id: int, current_user: User):
        booking = await self.db.bookings.get_one(id=booking_id)
        if current_user.role != "admin" and booking.user_id != current_user.id:
            raise ObjectNotFoundError("Booking not found")
        if booking.status == "cancelled":
            raise BookingAlreadyCancelledError()

        result = await self.db.bookings.update_status(booking_id, "cancelled")
        await self.db.commit()
        logger.info(
            "booking_cancelled booking_id=%s user_id=%s cancelled_by_user_id=%s",
            booking_id,
            booking.user_id,
            current_user.id,
        )
        return result
