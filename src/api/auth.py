from fastapi import APIRouter, Body, Response

from src.api.dependcencies import AuthServiceDep, UserIdDep
from src.schemas.users import UserRequestAdd

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])


@router.post("/register")
async def register_user(
    auth_service: AuthServiceDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "test_user",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                },
            }
        }
    ),
):
    await auth_service.register(data)
    return {"status": "ok"}


@router.post("/login")
async def login_user(
    auth_service: AuthServiceDep,
    response: Response,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "test_user",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                },
            }
        }
    ),
):
    access_token = await auth_service.login(data)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(
    auth_service: AuthServiceDep,
    user_id: UserIdDep,
):
    return await auth_service.get_user(user_id)


@router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(key="access_token")
    return {"status": "ok"}
