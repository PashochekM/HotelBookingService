from fastapi import APIRouter, Body, Response

from src.api.dependcencies import UserIdDep, DBDep
from src.exceptions import InvalidCredentialsError, ObjectAlreadyExistsError, ObjectNotFoundError
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])


@router.post("/register")
async def register_user(
    db: DBDep,
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
    existing_user = await db.users.get_user_with_hashed(email=data.email)
    if existing_user:
        raise ObjectAlreadyExistsError("User already exists")

    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    await db.users.add_one(new_user_data)
    await db.commit()
    return {"status": "ok"}


@router.post("/login")
async def login_user(
    db: DBDep,
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
    user = await db.users.get_user_with_hashed(email=data.email)

    if not user:
        raise InvalidCredentialsError()
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = AuthService().create_access_token({"id": user.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(
    db: DBDep,
    user_id: UserIdDep,
):
    user = await db.users.get_one_or_none(id=user_id)
    if user is None:
        raise ObjectNotFoundError("User not found")
    return user


@router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(key="access_token")
    return {"status": "bue!"}
