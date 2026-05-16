from typing import Annotated
from datetime import date

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from src.db import async_session_maker
from src.exceptions import InvalidBookingDatesError, InvalidTokenError
from src.services.auth import AuthService
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
    data = AuthService().decode_auth_token(token)
    user_id = data.get("id")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
