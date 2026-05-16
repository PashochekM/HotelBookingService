import logging

from fastapi import APIRouter, Body, Response

from src.api.dependcencies import UserIdDep, DBDep
from src.exceptions import InvalidCredentialsError, ObjectAlreadyExistsError, ObjectNotFoundError
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])


def mask_email(email: str) -> str:
    name, _, domain = email.partition("@")
    if not domain:
        return "***"
    return f"{name[:1]}***@{domain}"


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
        logger.warning("register_duplicate email=%s", mask_email(str(data.email)))
        raise ObjectAlreadyExistsError("User already exists")

    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    await db.users.add_one(new_user_data)
    await db.commit()
    logger.info("user_registered email=%s", mask_email(str(data.email)))
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
        logger.warning("login_failed reason=user_not_found email=%s", mask_email(str(data.email)))
        raise InvalidCredentialsError()
    if not AuthService().verify_password(data.password, user.hashed_password):
        logger.warning("login_failed reason=incorrect_password user_id=%s", user.id)
        raise InvalidCredentialsError()

    access_token = AuthService().create_access_token({"id": user.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    logger.info("login_success user_id=%s", user.id)
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
    logger.info("logout")
    return {"status": "bue!"}
