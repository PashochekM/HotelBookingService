from pydantic import BaseModel, Field, PositiveInt


class FacilityAdd(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class Facility(FacilityAdd):
    id: int


class RoomFacilityAdd(BaseModel):
    room_id: PositiveInt
    facility_id: PositiveInt


class RoomFacility(RoomFacilityAdd):
    id: int
