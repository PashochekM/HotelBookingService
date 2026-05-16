from datetime import date

from fastapi import APIRouter, Query, Body
from fastapi_cache.decorator import cache

from src.api.dependcencies import PaginationDep, DBDep
from src.schemas.hotels import HotelAdd, HotelPATCH

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.post("")
async def create_hotel(
        db: DBDep,
        hotel_data: HotelAdd = Body(openapi_examples={
    "1" : {
        "summary": "Сочи",
        "value" : {
            "title": "Hotel Sochi",
            "location": "Kabardinka"
        }
    },
    "2" : {
        "summary": "Base",
        "value" : {
            "title": "BaseHotel",
            "location": "BaseLocation"
        }
    }
})
):
    result = await db.hotels.add_one(hotel_data)
    await db.commit()
    return {"status": "ok", "data": result}


@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: date = Query(examples=["2026-08-01"]),
    date_to: date = Query(examples=["2026-08-10"]),
    title : str | None = Query(None, description="Название отеля"),
    location : str | None = Query(None, description="Локация"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_id}")
async def get_hotel(
        hotel_id: int,
        db: DBDep,
):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.put("/{hotel_id}")
async def edit_hotel(
        hotel_id: int,
        hotel_data: HotelAdd,
        db: DBDep,
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "ok"}


@router.delete("/{hotel_id}")
async def delete_hotel(
        hotel_id: int,
        db: DBDep,
):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "ok"}


@router.patch("/{hotel_id}")
async def partially_edit_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH,
        db: DBDep,
):
    await db.hotels.edit(hotel_data, patch=True, id=hotel_id)
    await db.commit()
    return {"status": "ok"}



 
