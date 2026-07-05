from fastapi import APIRouter, Query, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DateRangeDep, HotelsServiceDep, PaginationDep
from src.schemas.hotels import Hotel, HotelAdd, HotelPATCH
from src.schemas.responses import DataResponse

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.post("", response_model=DataResponse[Hotel])
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
    return {"data": result}


@router.get("", response_model=DataResponse[list[Hotel]])
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    date_range: DateRangeDep,
    hotels_service: HotelsServiceDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Локация"),
):
    hotels = await hotels_service.get_hotels(
        date_from=date_range.date_from,
        date_to=date_range.date_to,
        page=pagination.page,
        per_page=pagination.per_page,
        location=location,
        title=title,
    )
    return {"data": hotels}


@router.get("/{hotel_id}", response_model=DataResponse[Hotel])
async def get_hotel(
    hotel_id: int,
    hotels_service: HotelsServiceDep,
):
    hotel = await hotels_service.get_hotel(hotel_id)
    return {"data": hotel}


@router.put("/{hotel_id}", response_model=DataResponse[None])
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.edit_hotel(hotel_id, hotel_data)
    return {"data": None}


@router.delete("/{hotel_id}", response_model=DataResponse[None])
async def delete_hotel(
    hotel_id: int,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.delete_hotel(hotel_id)
    return {"data": None}


@router.patch("/{hotel_id}", response_model=DataResponse[None])
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPATCH,
    hotels_service: HotelsServiceDep,
):
    await hotels_service.partially_edit_hotel(hotel_id, hotel_data)
    return {"data": None}
