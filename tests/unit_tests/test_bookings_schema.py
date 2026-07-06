from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas.bookings import Booking, BookingRequestAdd


def test_booking_request_rejects_equal_dates():
    with pytest.raises(ValidationError):
        BookingRequestAdd(
            room_id=1,
            date_from=date(2026, 4, 23),
            date_to=date(2026, 4, 23),
        )


def test_booking_response_allows_legacy_equal_dates():
    booking = Booking(
        id=1,
        user_id=1,
        room_id=1,
        date_from=date(2026, 4, 23),
        date_to=date(2026, 4, 23),
        price=3000.0,
        status="active",
    )

    assert booking.date_from == booking.date_to
