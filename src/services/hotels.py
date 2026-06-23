import logging
from datetime import date

from src.schemas.hotels import HotelAdd, HotelPATCH
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class HotelsService(BaseService):
    async def create_hotel(self, hotel_data: HotelAdd):
        result = await self.db.hotels.add_one(hotel_data)
        await self.db.commit()
        logger.info("hotel_created hotel_id=%s title=%s", result.id, result.title)
        return result

    async def get_hotels(
        self,
        date_from: date,
        date_to: date,
        page: int,
        per_page: int | None,
        title: str | None,
        location: str | None,
    ):
        actual_per_page = per_page or 5
        return await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=actual_per_page,
            offset=actual_per_page * (page - 1),
        )

    async def get_hotel(self, hotel_id: int):
        return await self.db.hotels.get_one(id=hotel_id)

    async def edit_hotel(self, hotel_id: int, hotel_data: HotelAdd) -> None:
        await self.db.hotels.get_one(id=hotel_id)
        await self.db.hotels.edit(hotel_data, id=hotel_id)
        await self.db.commit()
        logger.info("hotel_updated hotel_id=%s patch=false", hotel_id)

    async def delete_hotel(self, hotel_id: int) -> None:
        await self.db.hotels.get_one(id=hotel_id)
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
        logger.info("hotel_deleted hotel_id=%s", hotel_id)

    async def partially_edit_hotel(self, hotel_id: int, hotel_data: HotelPATCH) -> None:
        if not hotel_data.model_dump(exclude_unset=True):
            return

        await self.db.hotels.edit(hotel_data, patch=True, id=hotel_id)
        await self.db.commit()
        logger.info("hotel_updated hotel_id=%s patch=true", hotel_id)
