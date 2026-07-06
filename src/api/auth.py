from fastapi import APIRouter, Body, Response

from src.api.dependencies import AuthServiceDep, CurrentUserDep
from src.schemas.responses import DataResponse, TokenResponse
from src.schemas.users import User, UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", response_model=DataResponse[None])
async def register_user(
    auth_service: AuthServiceDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Обычный пользователь",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                },
            },
            "2": {
                "summary": "Demo admin",
                "value": {
                    "email": "admin@mail.com",
                    "password": "admin",
                },
            },
        }
    ),
):
    await auth_service.register(data)
    return {"data": None}


@router.post("/login", response_model=DataResponse[TokenResponse])
async def login_user(
    auth_service: AuthServiceDep,
    response: Response,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Обычный пользователь",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                },
            },
            "2": {
                "summary": "Demo admin",
                "value": {
                    "email": "admin@mail.com",
                    "password": "admin",
                },
            },
        }
    ),
):
    access_token = await auth_service.login(data)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"data": {"access_token": access_token}}


@router.get("/me", response_model=DataResponse[User])
async def get_me(
    current_user: CurrentUserDep,
):
    return {"data": current_user}


@router.post("/logout", response_model=DataResponse[None])
async def logout(
    response: Response,
):
    response.delete_cookie(key="access_token")
    return {"data": None}
