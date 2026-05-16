from fastapi import APIRouter, Body, HTTPException, Response

from src.api.dependcencies import UserIdDep, DBDep
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аунтификация"])


@router.post("/register")
async def register_user(
        db: DBDep,
        data: UserRequestAdd = Body(openapi_examples={
            "1":{
                "summary": "test_user",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                }
            }
}),
):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    await db.users.add_one(new_user_data)
    await db.commit()
    return {"status": "ok"}


@router.post("/login")
async def login_user(
        db: DBDep,
        response: Response,
        data: UserRequestAdd = Body(openapi_examples={
            "1":{
                "summary": "test_user",
                "value": {
                    "email": "contact@mail.com",
                    "password": "pass",
                }
            }
})
):
    user = await db.users.get_user_with_hashed(email=data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Incorrect password")

    access_token = AuthService().create_access_token({'id': user.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token}

@router.get("/me")
async def get_me(
        db: DBDep,
        user_id: UserIdDep,
):
    return await db.users.get_one_or_none(id=user_id)


@router.post("/logout")
async def logout(
        response: Response,
):
    response.delete_cookie(key="access_token")
    return {"status": "bue!"}