from datetime import date

from fastapi import APIRouter, Body, HTTPException, Query

from src.api.dependcencies import DBDep
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomPATCH, RoomRequestAdd, RoomRequestPATCH

router = APIRouter(prefix="/hotels", tags=["Комнаты в отеле"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
        db: DBDep,
        hotel_id: int,
        date_from: date = Query(examples=["2026-08-01"]),
        date_to: date = Query(examples=["2026-08-10"]),
):
    return await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.post("/{hotel_id}/rooms")
async def create_room(
        db: DBDep,
        hotel_id: int,
        room_data: RoomRequestAdd = Body(openapi_examples={
            "1": {
                "summary": "Бомжарный",
                "value": {
                    "title": "Эконом",
                    "description": "Воняет пздц",
                    "price": 2000,
                    "quantity": 2,
                    "facilities": [1, 2]
                }
            },
            "2": {
                "summary": "Крутой",
                "value": {
                    "title": "Люкс",
                    "description": "Дорого богато",
                    "price": 100000,
                    "quantity": 5,
                    "facilities": [2]
                }
            }
        }),
):
    _room_to_add = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    result = await db.rooms.add_one(_room_to_add)

    rooms_facilities_data = [RoomFacilityAdd(room_id=result.id, facility_id=f_id) for f_id in room_data.facilities]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    return {"data": result}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
):
    room = await db.rooms.get_one_or_none_with_rels(hotel_id=hotel_id, id=room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_hotel(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomRequestAdd = Body(openapi_examples={
            "1": {
                "summary": "Бомжарный",
                "value": {
                    "title": "Эконом",
                    "description": "Воняет пздц",
                    "price": 1500,
                    "quantity": 2,
                    "facilities": [1]
                }
            },
            "2": {
                "summary": "Крутой",
                "value": {
                    "title": "Люкс",
                    "description": "Дорого богато",
                    "price": 30000,
                    "quantity": 6,
                    "facilities": [1]
                }
            }
        }),
):
    _room_to_edit = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())

    await db.rooms.edit(_room_to_edit, id=room_id, hotel_id=hotel_id)
    await db.rooms_facilities.set_room_facilities(room_id=room_id, f_ids=room_data.facilities)
    await db.commit()

    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
        db: DBDep,
        hotel_id: int,
        room_id: int
):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {"status": "ok"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomRequestPATCH = Body(openapi_examples={
            "1": {
                "summary": "Теперь средний",
                "value": {
                    "title": "Средний",
                    "price": 3000,
                }
            },
            "2": {
                "summary": "Изменений описания + количества",
                "value": {
                    "description": "Их много",
                    "quantity": 100,
                }
            }
        }),
):
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_to_edit = RoomPATCH(hotel_id=hotel_id, **_room_data_dict)
    await db.rooms.edit(_room_to_edit, patch=True, id=room_id)
    if "facilities" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(
            room_id=room_id,
            f_ids=_room_data_dict["facilities"]
        )
    await db.commit()
    return {"status": "ok"}
