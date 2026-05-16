import asyncio
import logging
from pathlib import Path

from time import sleep
from PIL import Image, UnidentifiedImageError

from src.db import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager

logger = logging.getLogger(__name__)


@celery_instance.task
def test_task():
    sleep(5)
    print("Test Task Completed")


# @celery_instance.task
def resize_image(image_path: str):
    sizes = [1000, 500, 200]
    image_path = Path(image_path)
    created_paths: list[Path] = []

    try:
        with Image.open(image_path) as img:
            name = image_path.stem
            ext = image_path.suffix

            for size in sizes:
                image_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)
                output_path = image_path.with_name(f"{name}_{size}px{ext}")
                image_resized.save(output_path)
                created_paths.append(output_path)
    except (FileNotFoundError, OSError, UnidentifiedImageError):
        for created_path in created_paths:
            created_path.unlink(missing_ok=True)
        logger.exception("Could not resize image %s", image_path)


async def booking_today_checkin_helper():
    print("Booking Today Checkin Task Started")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings=}")


@celery_instance.task(name="booking_today_checkin")
def booking_today_checkin():
    asyncio.run(booking_today_checkin_helper())
