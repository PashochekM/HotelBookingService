from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import RoomDataMapper
from src.repos.utils import rooms_ids_for_booking
from src.schemas.rooms import RoomWithRels


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        ##print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        ids_for_booking = await rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(ids_for_booking))
        )
        result = await self.session.execute(query)
        return [
            RoomWithRels.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]

    async def get_one_or_none_with_rels(self, **filters):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter_by(**filters)
        )
        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if res is None:
            return None
        return RoomWithRels.model_validate(res, from_attributes=True)
