import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from src import redis_manager
from src.api.dependcencies import get_db
from src.api.hotels import router as hotels_router
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from src.api.images import router as images_router


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
    #asyncio.create_task(run_send_emails_regularly())
    await redis_manager.connect()
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    await redis_manager.disconnect()




app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(facilities_router)
app.include_router(images_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)