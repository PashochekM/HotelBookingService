import logging

from fastapi import APIRouter, Body

from src.api.dependcencies import DateRangeDep, DBDep
from src.exceptions import ObjectNotFoundError, RelatedObjectNotFoundError
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomRequestAdd, RoomRequestPATCH

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hotels", tags=["Комнаты в отеле"])


async def validate_hotel_exists(db: DBDep, hotel_id: int):
    await db.hotels.get_one(id=hotel_id)


async def validate_facilities_exist(db: DBDep, facility_ids: list[int]):
    unique_facility_ids = list(set(facility_ids))
    existing_ids = await db.facilities.get_existing_ids(unique_facility_ids)
    missed_ids = set(unique_facility_ids) - existing_ids
    if missed_ids:
        raise RelatedObjectNotFoundError(f"Facilities not found: {sorted(missed_ids)}")


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_range: DateRangeDep,
):
    await validate_hotel_exists(db, hotel_id)
    return await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@router.post("/{hotel_id}/rooms")
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Бомжарный",
                "value": {
                    "title": "Эконом",
                    "description": "Воняет пздц",
                    "price": 2000,
                    "quantity": 2,
                    "facilities": [1, 2],
                },
            },
            "2": {
                "summary": "Крутой",
                "value": {
                    "title": "Люкс",
                    "description": "Дорого богато",
                    "price": 100000,
                    "quantity": 5,
                    "facilities": [2],
                },
            },
        }
    ),
):
    await validate_hotel_exists(db, hotel_id)
    await validate_facilities_exist(db, room_data.facilities)

    _room_to_add = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    result = await db.rooms.add_one(_room_to_add)

    rooms_facilities_data = [RoomFacilityAdd(room_id=result.id, facility_id=f_id) for f_id in room_data.facilities]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    logger.info("room_created room_id=%s hotel_id=%s facilities_count=%s", result.id, hotel_id, len(room_data.facilities))
    return {"data": result}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
):
    room = await db.rooms.get_one_or_none_with_rels(hotel_id=hotel_id, id=room_id)
    if room is None:
        raise ObjectNotFoundError("Room not found")

    return {"status": "ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_hotel(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Бомжарный",
                "value": {
                    "title": "Эконом",
                    "description": "Воняет пздц",
                    "price": 1500,
                    "quantity": 2,
                    "facilities": [1],
                },
            },
            "2": {
                "summary": "Крутой",
                "value": {
                    "title": "Люкс",
                    "description": "Дорого богато",
                    "price": 30000,
                    "quantity": 6,
                    "facilities": [1],
                },
            },
        }
    ),
):
    await validate_facilities_exist(db, room_data.facilities)
    _room_to_edit = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())

    await db.rooms.edit(_room_to_edit, id=room_id, hotel_id=hotel_id)
    await db.rooms_facilities.set_room_facilities(room_id=room_id, f_ids=room_data.facilities)
    await db.commit()
    logger.info("room_updated room_id=%s hotel_id=%s patch=false", room_id, hotel_id)

    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    logger.info("room_deleted room_id=%s hotel_id=%s", room_id, hotel_id)
    return {"status": "ok"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomRequestPATCH = Body(
        openapi_examples={
            "1": {
                "summary": "Теперь средний",
                "value": {
                    "title": "Средний",
                    "price": 3000,
                },
            },
            "2": {
                "summary": "Изменений описания + количества",
                "value": {
                    "description": "Их много",
                    "quantity": 100,
                },
            },
        }
    ),
):
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    if not _room_data_dict:
        return {"status": "ok"}
    if "facilities" in _room_data_dict:
        await validate_facilities_exist(db, _room_data_dict["facilities"])

    room_fields = {key: value for key, value in _room_data_dict.items() if key != "facilities"}
    if room_fields:
        _room_to_edit = RoomPATCH(**room_fields)
        await db.rooms.edit(_room_to_edit, patch=True, id=room_id, hotel_id=hotel_id)
    else:
        await db.rooms.get_one(id=room_id, hotel_id=hotel_id)
    if "facilities" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(room_id=room_id, f_ids=_room_data_dict["facilities"])
    await db.commit()
    logger.info("room_updated room_id=%s hotel_id=%s patch=true", room_id, hotel_id)
    return {"status": "ok"}
