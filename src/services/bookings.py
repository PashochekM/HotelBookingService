import logging

from src.schemas.bookings import BookingAdd, BookingRequestAdd
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
