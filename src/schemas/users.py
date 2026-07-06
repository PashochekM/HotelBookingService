from typing import Literal

from pydantic import BaseModel, EmailStr, Field

UserRole = Literal["user", "admin"]


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str
    role: UserRole = "user"


class User(BaseModel):
    id: int
    email: str
    role: UserRole


class UserWithHashedPassword(User):
    hashed_password: str
