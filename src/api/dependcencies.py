from typing import Annotated
from fastapi import Depends, Query, Request, HTTPException
from pydantic import BaseModel
from starlette import status

from src.db import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]

PaginationDep = Annotated[PaginationParams, Depends()]

def get_token(request: Request) -> str :
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет токена доступа",
        )
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_auth_token(token)
    user_id = data.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]