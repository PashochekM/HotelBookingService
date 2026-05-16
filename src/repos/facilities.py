from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper




class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    schema = RoomFacility

    async def set_room_facilities(self, room_id: int, f_ids: list[int]):
        get_current_f_ids = (
            select(self.model.facility_id)
            .filter_by(room_id=room_id)
        )
        result = await self.session.execute(get_current_f_ids)
        current_facilities_ids: list[int] = result.scalars().all()
        ids_to_delete: list[int] = list(set(current_facilities_ids) - set(f_ids))
        ids_to_append: list[int] = list(set(f_ids) - set(current_facilities_ids))

        if ids_to_delete:
            delete_m2m_f_stmt = (
                delete(self.model)
                .filter(
                    self.model.room_id == room_id,
                    self.model.facility_id.in_(ids_to_delete)
                )
            )
            await self.session.execute(delete_m2m_f_stmt)

        if ids_to_append:
            insert_m2m_f_stmt = (
                insert(self.model)
                .values([{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_append])
            )
            await self.session.execute(insert_m2m_f_stmt)




