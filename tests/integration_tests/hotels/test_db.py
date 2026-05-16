from src.schemas.hotels import HotelAdd


async def test_add_hotel(db):
    hotel_data = HotelAdd(
        title="Hotel 5 stars",
        location="Berlin",
    )
    await db.hotels.add_one(hotel_data)
    await db.commit()




