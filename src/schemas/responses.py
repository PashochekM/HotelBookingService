from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    data: T


class TokenResponse(BaseModel):
    access_token: str


class UploadedImageResponse(BaseModel):
    filename: str
