from pydantic import BaseModel, EmailStr, Field


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: str


class UserWithHashedPassword(User):
    hashed_password: str
