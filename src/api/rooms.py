from fastapi import APIRouter, Body

from src.api.dependcencies import DateRangeDep, RoomsServiceDep
from src.schemas.rooms import RoomRequestAdd, RoomRequestPATCH

router = APIRouter(prefix="/hotels", tags=["Комнаты в отеле"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    date_range: DateRangeDep,
):
    return await rooms_service.get_rooms(
        hotel_id=hotel_id,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )


@router.post("/{hotel_id}/rooms")
async def create_room(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_data: RoomRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Эконом",
                "value": {
                    "title": "Эконом",
                    "description": "Компактный номер с базовыми удобствами",
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
    result = await rooms_service.create_room(hotel_id, room_data)
    return {"data": result}


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_id: int,
):
    room = await rooms_service.get_room(hotel_id, room_id)
    return {"status": "ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_hotel(   
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Эконом",
                "value": {
                    "title": "Эконом",
                    "description": "Компактный номер с базовыми удобствами",
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
    await rooms_service.edit_room(hotel_id, room_id, room_data)
    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(rooms_service: RoomsServiceDep, hotel_id: int, room_id: int):
    await rooms_service.delete_room(hotel_id, room_id)
    return {"status": "ok"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
    rooms_service: RoomsServiceDep,
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
    await rooms_service.partially_edit_room(hotel_id, room_id, room_data)
    return {"status": "ok"}
