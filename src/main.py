import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette import status

from src import redis_manager
from src.api.dependcencies import get_db
from src.api.hotels import router as hotels_router
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from src.api.images import router as images_router
from src.exceptions import (
    DatabaseIntegrityError,
    InfrastructureError,
    InvalidBookingDatesError,
    InvalidCredentialsError,
    InvalidImageError,
    InvalidTokenError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    RelatedObjectNotFoundError,
    RoomNotAvailableError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


async def send_emails_bookings_today_checkin():
    async for db in get_db():
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings=}")


async def run_send_emails_regularly():
    while True:
        await send_emails_bookings_today_checkin()
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # asyncio.create_task(run_send_emails_regularly())
    try:
        await redis_manager.connect()
    except InfrastructureError:
        logger.warning("Redis is unavailable. API is starting without Redis.", exc_info=True)
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    await redis_manager.disconnect()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ObjectNotFoundError)
async def object_not_found_handler(_: Request, exc: ObjectNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


@app.exception_handler(RelatedObjectNotFoundError)
async def related_object_not_found_handler(_: Request, exc: RelatedObjectNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


@app.exception_handler(ObjectAlreadyExistsError)
async def object_already_exists_handler(_: Request, exc: ObjectAlreadyExistsError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(RoomNotAvailableError)
async def room_not_available_handler(_: Request, exc: RoomNotAvailableError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(InvalidBookingDatesError)
async def invalid_booking_dates_handler(_: Request, exc: InvalidBookingDatesError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.message})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exc.message})


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(_: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(TokenExpiredError)
async def token_expired_handler(_: Request, exc: TokenExpiredError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(InvalidImageError)
async def invalid_image_handler(_: Request, exc: InvalidImageError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message})


@app.exception_handler(DatabaseIntegrityError)
async def database_integrity_handler(_: Request, exc: DatabaseIntegrityError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(InfrastructureError)
async def infrastructure_handler(_: Request, exc: InfrastructureError):
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": exc.message})


app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(facilities_router)
app.include_router(images_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
