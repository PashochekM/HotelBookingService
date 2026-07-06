from datetime import date
from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from src.db import async_session_maker
from src.exceptions import ForbiddenError, InvalidBookingDatesError, InvalidTokenError
from src.schemas.users import User
from src.services.auth import AuthService
from src.services.bookings import BookingsService
from src.services.facilities import FacilitiesService
from src.services.hotels import HotelsService
from src.services.images import ImagesService
from src.services.rooms import RoomsService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


class DateRangeParams(BaseModel):
    date_from: date
    date_to: date

    def validate_dates(self):
        if self.date_to <= self.date_from:
            raise InvalidBookingDatesError()
        return self


def get_date_range(
    date_from: date = Query(examples=["2026-08-01"]),
    date_to: date = Query(examples=["2026-08-10"]),
) -> DateRangeParams:
    return DateRangeParams(date_from=date_from, date_to=date_to).validate_dates()


DateRangeDep = Annotated[DateRangeParams, Depends(get_date_range)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise InvalidTokenError("No access token")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService.decode_auth_token(token)
    user_id = data.get("id")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_current_user(user_id: UserIdDep, db: DBDep) -> User:
    user = await db.users.get_one_or_none(id=user_id)
    if user is None:
        raise InvalidTokenError("User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_admin(current_user: CurrentUserDep) -> User:
    if current_user.role != "admin":
        raise ForbiddenError("Admin privileges required")
    return current_user


AdminDep = Annotated[User, Depends(require_admin)]


def get_auth_service(db: DBDep) -> AuthService:
    return AuthService(db)


def get_hotels_service(db: DBDep) -> HotelsService:
    return HotelsService(db)


def get_rooms_service(db: DBDep) -> RoomsService:
    return RoomsService(db)


def get_bookings_service(db: DBDep) -> BookingsService:
    return BookingsService(db)


def get_facilities_service(db: DBDep) -> FacilitiesService:
    return FacilitiesService(db)


def get_images_service() -> ImagesService:
    return ImagesService()


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
HotelsServiceDep = Annotated[HotelsService, Depends(get_hotels_service)]
RoomsServiceDep = Annotated[RoomsService, Depends(get_rooms_service)]
BookingsServiceDep = Annotated[BookingsService, Depends(get_bookings_service)]
FacilitiesServiceDep = Annotated[FacilitiesService, Depends(get_facilities_service)]
ImagesServiceDep = Annotated[ImagesService, Depends(get_images_service)]
