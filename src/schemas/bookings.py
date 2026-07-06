from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, PositiveInt, model_validator

BookingStatus = Literal["active", "cancelled"]


class BookingBase(BaseModel):
    room_id: PositiveInt
    date_from: date
    date_to: date


class BookingRequestAdd(BookingBase):
    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_to <= self.date_from:
            raise ValueError("date_to must be later than date_from")
        return self


class BookingAdd(BookingRequestAdd):
    user_id: PositiveInt
    price: float = Field(gt=0)
    status: BookingStatus = "active"


class Booking(BookingBase):
    id: int
    user_id: int
    price: float
    status: BookingStatus


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingPATCH(BaseModel):
    room_id: PositiveInt | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)
    price: float | None = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from and self.date_to and self.date_to <= self.date_from:
            raise ValueError("date_to must be later than date_from")
        return self
