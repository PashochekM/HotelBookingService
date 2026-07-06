import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import async_session_maker
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repos.facilities import RoomsFacilitiesRepository
from src.services.auth import AuthService

DEMO_ADMIN_EMAIL = "admin@mail.com"
DEMO_ADMIN_PASSWORD = "admin"

DEMO_FACILITIES = [
    "Wi-Fi",
    "Parking",
    "Breakfast",
    "Sea view",
    "Spa",
]

DEMO_HOTELS = [
    {
        "title": "Aurora City Hotel",
        "location": "Moscow",
        "rooms": [
            {
                "title": "Standard Double",
                "description": "Compact room with one double bed and a city view.",
                "price": 4500,
                "quantity": 8,
                "facilities": ["Wi-Fi", "Breakfast"],
            },
            {
                "title": "Business Suite",
                "description": "Spacious suite with a work desk and separate lounge area.",
                "price": 9200,
                "quantity": 3,
                "facilities": ["Wi-Fi", "Parking", "Breakfast"],
            },
        ],
    },
    {
        "title": "Nevsky Grand",
        "location": "Saint Petersburg",
        "rooms": [
            {
                "title": "Classic Twin",
                "description": "Room with two single beds near the historic center.",
                "price": 5200,
                "quantity": 6,
                "facilities": ["Wi-Fi"],
            },
            {
                "title": "Canal View Deluxe",
                "description": "Deluxe room with a large bed and canal view.",
                "price": 8700,
                "quantity": 4,
                "facilities": ["Wi-Fi", "Breakfast", "Spa"],
            },
        ],
    },
    {
        "title": "Black Sea Residence",
        "location": "Sochi",
        "rooms": [
            {
                "title": "Sea View Room",
                "description": "Bright room with balcony and sea view.",
                "price": 7600,
                "quantity": 10,
                "facilities": ["Wi-Fi", "Sea view", "Breakfast"],
            },
            {
                "title": "Family Apartment",
                "description": "Two-room apartment for families with children.",
                "price": 11800,
                "quantity": 5,
                "facilities": ["Wi-Fi", "Parking", "Sea view"],
            },
        ],
    },
    {
        "title": "Altai Pine Lodge",
        "location": "Gorno-Altaysk",
        "rooms": [
            {
                "title": "Forest Cabin",
                "description": "Quiet wooden cabin with mountain and forest views.",
                "price": 6800,
                "quantity": 7,
                "facilities": ["Wi-Fi", "Parking"],
            },
            {
                "title": "Panorama Chalet",
                "description": "Premium chalet with fireplace and panoramic windows.",
                "price": 14500,
                "quantity": 2,
                "facilities": ["Wi-Fi", "Parking", "Spa"],
            },
        ],
    },
]


async def get_demo_admin(session: AsyncSession) -> UsersOrm:
    query = select(UsersOrm).where(UsersOrm.email == DEMO_ADMIN_EMAIL).limit(1)
    result = await session.execute(query)
    user = result.scalars().first()
    hashed_password = AuthService.hash_password(DEMO_ADMIN_PASSWORD)

    if user is None:
        user = UsersOrm(
            email=DEMO_ADMIN_EMAIL,
            hashed_password=hashed_password,
            role="admin",
        )
        session.add(user)
    else:
        user.hashed_password = hashed_password
        user.role = "admin"

    return user


async def get_or_create_facility(session: AsyncSession, title: str) -> FacilitiesOrm:
    query = select(FacilitiesOrm).where(FacilitiesOrm.title == title).limit(1)
    result = await session.execute(query)
    facility = result.scalars().first()
    if facility is None:
        facility = FacilitiesOrm(title=title)
        session.add(facility)
        await session.flush()
    return facility


async def get_or_create_hotel(session: AsyncSession, title: str, location: str) -> HotelsOrm:
    query = select(HotelsOrm).where(HotelsOrm.title == title, HotelsOrm.location == location).limit(1)
    result = await session.execute(query)
    hotel = result.scalars().first()
    if hotel is None:
        hotel = HotelsOrm(title=title, location=location)
        session.add(hotel)
        await session.flush()
    return hotel


async def get_or_create_room(session: AsyncSession, hotel_id: int, room_data: dict) -> RoomsOrm:
    query = select(RoomsOrm).where(RoomsOrm.hotel_id == hotel_id, RoomsOrm.title == room_data["title"]).limit(1)
    result = await session.execute(query)
    room = result.scalars().first()
    if room is None:
        room = RoomsOrm(
            hotel_id=hotel_id,
            title=room_data["title"],
            description=room_data["description"],
            price=room_data["price"],
            quantity=room_data["quantity"],
        )
        session.add(room)
        await session.flush()
    else:
        room.description = room_data["description"]
        room.price = room_data["price"]
        room.quantity = room_data["quantity"]
    return room


async def seed_demo() -> None:
    async with async_session_maker() as session:
        await get_demo_admin(session)
        facilities_by_title = {}
        for title in DEMO_FACILITIES:
            facilities_by_title[title] = await get_or_create_facility(session, title)

        room_facilities_repo = RoomsFacilitiesRepository(session)
        hotels_count = 0
        rooms_count = 0

        for hotel_data in DEMO_HOTELS:
            hotel = await get_or_create_hotel(
                session=session,
                title=hotel_data["title"],
                location=hotel_data["location"],
            )
            hotels_count += 1

            for room_data in hotel_data["rooms"]:
                room = await get_or_create_room(session, hotel.id, room_data)
                facility_ids = [facilities_by_title[title].id for title in room_data["facilities"]]
                await room_facilities_repo.set_room_facilities(room_id=room.id, f_ids=facility_ids)
                rooms_count += 1

        await session.commit()

    print("Demo data is ready.")
    print(f"Admin: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")
    print(f"Facilities: {len(DEMO_FACILITIES)}")
    print(f"Hotels: {hotels_count}")
    print(f"Rooms: {rooms_count}")


if __name__ == "__main__":
    asyncio.run(seed_demo())
