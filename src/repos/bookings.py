import logging
from datetime import date

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.exceptions import (
    DatabaseIntegrityError,
    InvalidBookingDatesError,
    ObjectNotFoundError,
    RelatedObjectNotFoundError,
    RoomNotAvailableError,
)
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import BookingDataMapper
from src.repos.utils import rooms_ids_for_booking
from src.schemas.bookings import BookingAdd, Booking

logger = logging.getLogger(__name__)


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).filter(
            self.model.date_from == date.today(),
            self.model.status == "active",
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def update_status(self, booking_id: int, status: str) -> Booking:
        stmt = update(self.model).filter_by(id=booking_id).values(status=status).returning(self.model)
        result = await self.session.execute(stmt)
        res = result.scalars().one_or_none()
        if res is None:
            raise ObjectNotFoundError("Booking not found")
        return self.mapper.map_to_domain_entity(res)

    async def add_booking(self, data: BookingAdd) -> Booking:
        if data.date_to <= data.date_from:
            logger.info("booking_invalid_dates room_id=%s date_from=%s date_to=%s", data.room_id, data.date_from, data.date_to)
            raise InvalidBookingDatesError()

        lock_room_query = select(RoomsOrm.id).filter_by(id=data.room_id).with_for_update()
        await self.session.execute(lock_room_query)

        query = await rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
        )
        rooms_ids = (await self.session.execute(query)).scalars().all()

        if data.room_id not in rooms_ids:
            logger.info("booking_room_unavailable room_id=%s date_from=%s date_to=%s", data.room_id, data.date_from, data.date_to)
            raise RoomNotAvailableError()

        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            detail = str(exc.orig).lower()
            if "foreign key" in detail:
                logger.warning("booking_integrity_error type=foreign_key room_id=%s user_id=%s", data.room_id, data.user_id)
                raise RelatedObjectNotFoundError("Room or user not found") from exc
            logger.error("booking_integrity_error type=unknown room_id=%s user_id=%s", data.room_id, data.user_id, exc_info=True)
            raise DatabaseIntegrityError() from exc
        res = result.scalars().one()
        return self.mapper.map_to_domain_entity(res)
