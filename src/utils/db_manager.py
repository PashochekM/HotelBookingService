from sqlalchemy.exc import IntegrityError

from src.exceptions import DatabaseIntegrityError, ObjectAlreadyExistsError, RelatedObjectNotFoundError
from src.repos.bookings import BookingsRepository
from src.repos.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.repos.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            detail = str(exc.orig).lower()
            if "unique" in detail or "duplicate" in detail:
                raise ObjectAlreadyExistsError("Object already exists") from exc
            if "foreign key" in detail:
                raise RelatedObjectNotFoundError("Related object not found") from exc
            raise DatabaseIntegrityError() from exc
