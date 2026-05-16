import os
import asyncio

from time import sleep
from PIL import Image

from src.db import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager


@celery_instance.task
def test_task():
    sleep(5)
    print("Test Task Completed")


# @celery_instance.task
def resize_image(image_path: str):
    sizes = [1000, 500, 200]
    img = Image.open(image_path)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    for size in sizes:
        image_resized = img.resize((size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS)
        new_name = f"{name}_{size}px{ext}"
        output_path = f"src/static/images/{new_name}"
        image_resized.save(output_path)


async def booking_today_checkin_helper():
    print("Booking Today Checkin Task Started")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"{bookings=}")


@celery_instance.task(name="booking_today_checkin")
def booking_today_checkin():
    asyncio.run(booking_today_checkin_helper())
