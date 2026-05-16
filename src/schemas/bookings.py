from pydantic import BaseModel, Field
from datetime import date
from pydantic import PositiveInt, model_validator


class BookingRequestAdd(BaseModel):
    room_id: PositiveInt
    date_from: date
    date_to: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_to <= self.date_from:
            raise ValueError("date_to must be later than date_from")
        return self


class BookingAdd(BookingRequestAdd):
    user_id: PositiveInt
    price: int = Field(gt=0)


class Booking(BookingAdd):
    id: int


class BookingPATCH(BaseModel):
    room_id: PositiveInt | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)
    price: int | None = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from and self.date_to and self.date_to <= self.date_from:
            raise ValueError("date_to must be later than date_from")
        return self
