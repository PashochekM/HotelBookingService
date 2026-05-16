from datetime import date

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.exceptions import DatabaseIntegrityError, InvalidBookingDatesError, RelatedObjectNotFoundError, RoomNotAvailableError
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import BookingDataMapper
from src.repos.utils import rooms_ids_for_booking
from src.schemas.bookings import BookingAdd, Booking


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).filter(self.model.date_from == date.today())
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, data: BookingAdd) -> Booking:
        if data.date_to <= data.date_from:
            raise InvalidBookingDatesError()

        lock_room_query = select(RoomsOrm.id).filter_by(id=data.room_id).with_for_update()
        await self.session.execute(lock_room_query)

        query = await rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
        )
        rooms_ids = (await self.session.execute(query)).scalars().all()

        if data.room_id not in rooms_ids:
            raise RoomNotAvailableError()

        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            detail = str(exc.orig).lower()
            if "foreign key" in detail:
                raise RelatedObjectNotFoundError("Room or user not found") from exc
            raise DatabaseIntegrityError() from exc
        res = result.scalars().one()
        return self.mapper.map_to_domain_entity(res)
