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
from src.api.dependencies import get_db
from src.api.health import router as health_router
from src.api.hotels import router as hotels_router
from src.api.middlewares import request_logging_middleware
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from src.api.images import router as images_router
from src.config import settings
from src.exceptions import (
    BookingAlreadyCancelledError,
    DatabaseIntegrityError,
    ForbiddenError,
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
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def send_emails_bookings_today_checkin():
    async for db in get_db():
        bookings = await db.bookings.get_bookings_with_today_checkin()
        logger.info("today_checkin_bookings_loaded count=%s", len(bookings))


async def run_send_emails_regularly():
    while True:
        await send_emails_bookings_today_checkin()
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application_starting mode=%s", settings.MODE)
    # asyncio.create_task(run_send_emails_regularly())
    try:
        await redis_manager.connect()
    except InfrastructureError:
        logger.warning("Redis is unavailable. API is starting without Redis.", exc_info=True)
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    await redis_manager.disconnect()
    logger.info("application_stopped")


app = FastAPI(lifespan=lifespan)
app.middleware("http")(request_logging_middleware)


@app.exception_handler(ObjectNotFoundError)
async def object_not_found_handler(request: Request, exc: ObjectNotFoundError):
    logger.info("object_not_found path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


@app.exception_handler(RelatedObjectNotFoundError)
async def related_object_not_found_handler(request: Request, exc: RelatedObjectNotFoundError):
    logger.info("related_object_not_found path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})


@app.exception_handler(ObjectAlreadyExistsError)
async def object_already_exists_handler(request: Request, exc: ObjectAlreadyExistsError):
    logger.warning("object_already_exists path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(RoomNotAvailableError)
async def room_not_available_handler(request: Request, exc: RoomNotAvailableError):
    logger.info("room_not_available path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(BookingAlreadyCancelledError)
async def booking_already_cancelled_handler(request: Request, exc: BookingAlreadyCancelledError):
    logger.info("booking_already_cancelled path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(InvalidBookingDatesError)
async def invalid_booking_dates_handler(request: Request, exc: InvalidBookingDatesError):
    logger.info("invalid_booking_dates path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.message})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    logger.warning("invalid_credentials path=%s", request.url.path)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exc.message})


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    logger.warning("invalid_token path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    logger.warning("forbidden path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": exc.message})


@app.exception_handler(TokenExpiredError)
async def token_expired_handler(request: Request, exc: TokenExpiredError):
    logger.warning("token_expired path=%s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(InvalidImageError)
async def invalid_image_handler(request: Request, exc: InvalidImageError):
    logger.warning("invalid_image path=%s detail=%s", request.url.path, exc.message)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message})


@app.exception_handler(DatabaseIntegrityError)
async def database_integrity_handler(request: Request, exc: DatabaseIntegrityError):
    logger.error("database_integrity_error path=%s detail=%s", request.url.path, exc.message, exc_info=True)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})


@app.exception_handler(InfrastructureError)
async def infrastructure_handler(request: Request, exc: InfrastructureError):
    logger.error("infrastructure_error path=%s detail=%s", request.url.path, exc.message, exc_info=True)
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception path=%s", request.url.path)
    response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(facilities_router)
app.include_router(images_router)
app.include_router(health_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
