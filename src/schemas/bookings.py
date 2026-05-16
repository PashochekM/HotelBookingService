from pydantic import BaseModel, Field
from datetime import date


class BookingRequestAdd(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class BookingAdd(BookingRequestAdd):
    user_id: int
    price: int


class Booking(BookingAdd):
    id: int


class BookingPATCH(BaseModel):
    room_id: int | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)
    price: int | None = Field(None)

