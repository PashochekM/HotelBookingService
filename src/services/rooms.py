import logging
from datetime import date

from src.exceptions import ObjectNotFoundError, RelatedObjectNotFoundError
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomRequestAdd, RoomRequestPATCH
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class RoomsService(BaseService):
    async def validate_hotel_exists(self, hotel_id: int) -> None:
        await self.db.hotels.get_one(id=hotel_id)

    async def validate_facilities_exist(self, facility_ids: list[int]) -> None:
        unique_facility_ids = list(set(facility_ids))
        existing_ids = await self.db.facilities.get_existing_ids(unique_facility_ids)
        missed_ids = set(unique_facility_ids) - existing_ids
        if missed_ids:
            raise RelatedObjectNotFoundError(f"Facilities not found: {sorted(missed_ids)}")

    async def get_rooms(self, hotel_id: int, date_from: date, date_to: date):
        await self.validate_hotel_exists(hotel_id)
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id,
            date_from=date_from,
            date_to=date_to,
        )

    async def create_room(self, hotel_id: int, room_data: RoomRequestAdd):
        await self.validate_hotel_exists(hotel_id)
        await self.validate_facilities_exist(room_data.facilities)

        room_to_add = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        result = await self.db.rooms.add_one(room_to_add)
        rooms_facilities_data = [RoomFacilityAdd(room_id=result.id, facility_id=f_id) for f_id in room_data.facilities]
        await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()
        logger.info("room_created room_id=%s hotel_id=%s facilities_count=%s", result.id, hotel_id, len(room_data.facilities))
        return result

    async def get_room(self, hotel_id: int, room_id: int):
        room = await self.db.rooms.get_one_or_none_with_rels(hotel_id=hotel_id, id=room_id)
        if room is None:
            raise ObjectNotFoundError("Room not found")
        return room

    async def edit_room(self, hotel_id: int, room_id: int, room_data: RoomRequestAdd) -> None:
        await self.validate_facilities_exist(room_data.facilities)
        room_to_edit = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await self.db.rooms.edit(room_to_edit, id=room_id, hotel_id=hotel_id)
        await self.db.rooms_facilities.set_room_facilities(room_id=room_id, f_ids=room_data.facilities)
        await self.db.commit()
        logger.info("room_updated room_id=%s hotel_id=%s patch=false", room_id, hotel_id)

    async def delete_room(self, hotel_id: int, room_id: int) -> None:
        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.commit()
        logger.info("room_deleted room_id=%s hotel_id=%s", room_id, hotel_id)

    async def partially_edit_room(self, hotel_id: int, room_id: int, room_data: RoomRequestPATCH) -> None:
        room_data_dict = room_data.model_dump(exclude_unset=True)
        if not room_data_dict:
            return

        if "facilities" in room_data_dict:
            await self.validate_facilities_exist(room_data_dict["facilities"])

        room_fields = {key: value for key, value in room_data_dict.items() if key != "facilities"}
        if room_fields:
            room_to_edit = RoomPATCH(**room_fields)
            await self.db.rooms.edit(room_to_edit, patch=True, id=room_id, hotel_id=hotel_id)
        else:
            await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)

        if "facilities" in room_data_dict:
            await self.db.rooms_facilities.set_room_facilities(room_id=room_id, f_ids=room_data_dict["facilities"])

        await self.db.commit()
        logger.info("room_updated room_id=%s hotel_id=%s patch=true", room_id, hotel_id)
