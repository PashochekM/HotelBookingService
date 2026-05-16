from datetime import date

from sqlalchemy import select

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import HotelDataMapper
from src.repos.utils import rooms_ids_for_booking


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper


    async def get_filtered_by_time(
            self,
            date_from: date,
            date_to: date,
            location,
            title,
            limit=None,
            offset=None
    ):
        rooms_ids_to_get = await rooms_ids_for_booking(date_from, date_to)
        hotels_ids = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids))
        if location:
            query = query.where(HotelsOrm.location.ilike(f"%{location}%"))
        if title:
            query = query.where(HotelsOrm.title.ilike(f"%{title}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(hotel)
            for hotel in result.scalars().all()
        ]


