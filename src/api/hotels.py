from fastapi import APIRouter, Query, Body
from fastapi_cache.decorator import cache

from src.api.dependcencies import DateRangeDep, HotelsServiceDep, PaginationDep
from src.schemas.hotels import HotelAdd, HotelPATCH

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.post("")
async def create_hotel(
    hotels_service: HotelsServiceDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {"title": "Hotel Sochi", "location": "Kabardinka"},
            },
            "2": {
                "summary": "Base",
                "value": {"title": "BaseHotel", "location": "BaseLocation"},
            },
        }
    ),
):
    result = await hotels_service.create_hotel(hotel_data)
    return {"status": "ok", "data": result}


@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    date_range: DateRangeDep,
    hotels_service: HotelsServiceDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Локация"),
):
    return await hotels_service.get_hotels(
        date_from=date_range.date_from,
        date_to=date_range.date_to,
        page=pagination.page,
        per_page=pagination.per_page,
        location=location,
        title=title,
    )


@router.get("/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    hotels_service: HotelsServiceDep,
):
    return await hotels_service.get_hotel(hotel_id)


@router.put("/{hotel_id}")
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.edit_hotel(hotel_id, hotel_data)
    return {"status": "ok"}


@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.delete_hotel(hotel_id)
    return {"status": "ok"}


@router.patch("/{hotel_id}")
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPATCH,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.partially_edit_hotel(hotel_id, hotel_data)
    return {"status": "ok"}
