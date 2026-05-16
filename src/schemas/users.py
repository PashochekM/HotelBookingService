from pydantic import BaseModel, EmailStr


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: str


class UserWithHashedPassword(User):
    hashed_password: str