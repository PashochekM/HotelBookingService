from fastapi import APIRouter, Body

from src.api.dependencies import AdminDep, DateRangeDep, RoomsServiceDep
from src.schemas.responses import DataResponse
from src.schemas.rooms import Room, RoomRequestAdd, RoomRequestPATCH, RoomWithRels

router = APIRouter(prefix="/hotels", tags=["Комнаты"])


@router.get("/{hotel_id}/rooms", response_model=DataResponse[list[RoomWithRels]])
async def get_rooms(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    date_range: DateRangeDep,
):
    rooms = await rooms_service.get_rooms(
        hotel_id=hotel_id,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    return {"data": rooms}


@router.post("/{hotel_id}/rooms", response_model=DataResponse[Room])
async def create_room(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    _admin: AdminDep,
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
                "summary": "Люкс",
                "value": {
                    "title": "Люкс",
                    "description": "Просторный номер повышенной комфортности",
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


@router.get("/{hotel_id}/rooms/{room_id}", response_model=DataResponse[RoomWithRels])
async def get_room(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_id: int,
):
    room = await rooms_service.get_room(hotel_id, room_id)
    return {"data": room}


@router.put("/{hotel_id}/rooms/{room_id}", response_model=DataResponse[None])
async def edit_hotel(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_id: int,
    _admin: AdminDep,
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
                "summary": "Люкс",
                "value": {
                    "title": "Люкс",
                    "description": "Просторный номер повышенной комфортности",
                    "price": 30000,
                    "quantity": 6,
                    "facilities": [1],
                },
            },
        }
    ),
):
    await rooms_service.edit_room(hotel_id, room_id, room_data)
    return {"data": None}


@router.delete("/{hotel_id}/rooms/{room_id}", response_model=DataResponse[None])
async def delete_room(rooms_service: RoomsServiceDep, hotel_id: int, room_id: int, _admin: AdminDep):
    await rooms_service.delete_room(hotel_id, room_id)
    return {"data": None}


@router.patch("/{hotel_id}/rooms/{room_id}", response_model=DataResponse[None])
async def partially_edit_room(
    rooms_service: RoomsServiceDep,
    hotel_id: int,
    room_id: int,
    _admin: AdminDep,
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
                "summary": "Изменение описания и количества",
                "value": {
                    "description": "Номеров много",
                    "quantity": 100,
                },
            },
        }
    ),
):
    await rooms_service.partially_edit_room(hotel_id, room_id, room_data)
    return {"data": None}
