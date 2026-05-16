from pydantic import BaseModel, Field, PositiveInt

from src.schemas.facilities import Facility


class RoomRequestAdd(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None)
    price: int = Field(gt=0)
    quantity: int = Field(gt=0)
    facilities: list[PositiveInt] = Field(default_factory=list)


class RoomAdd(BaseModel):
    hotel_id: PositiveInt
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None)
    price: int = Field(gt=0)
    quantity: int = Field(gt=0)


class Room(RoomAdd):
    id: int


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomRequestPATCH(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None)
    price: int | None = Field(None, gt=0)
    quantity: int | None = Field(None, gt=0)
    facilities: list[PositiveInt] = Field(default_factory=list)


class RoomPATCH(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None)
    price: int | None = Field(None, gt=0)
    quantity: int | None = Field(None, gt=0)
