import logging
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.config import settings
from src.exceptions import InvalidCredentialsError, InvalidTokenError, ObjectAlreadyExistsError, ObjectNotFoundError, TokenExpiredError
from src.schemas.users import UserAdd, UserRequestAdd
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def mask_email(email: str) -> str:
        name, _, domain = email.partition("@")
        if not domain:
            return "***"
        return f"{name[:1]}***@{domain}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def decode_auth_token(cls, auth_token: str) -> dict:
        try:
            data = jwt.decode(auth_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc
        except jwt.exceptions.InvalidTokenError as exc:
            raise InvalidTokenError() from exc
        return data

    async def register(self, data: UserRequestAdd) -> None:
        existing_user = await self.db.users.get_user_with_hashed(email=data.email)
        if existing_user:
            logger.warning("register_duplicate email=%s", self.mask_email(str(data.email)))
            raise ObjectAlreadyExistsError("User already exists")

        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        await self.db.users.add_one(new_user_data)
        await self.db.commit()
        logger.info("user_registered email=%s", self.mask_email(str(data.email)))

    async def login(self, data: UserRequestAdd) -> str:
        user = await self.db.users.get_user_with_hashed(email=data.email)

        if not user:
            logger.warning("login_failed reason=user_not_found email=%s", self.mask_email(str(data.email)))
            raise InvalidCredentialsError()
        if not self.verify_password(data.password, user.hashed_password):
            logger.warning("login_failed reason=incorrect_password user_id=%s", user.id)
            raise InvalidCredentialsError()

        access_token = self.create_access_token({"id": user.id})
        logger.info("login_success user_id=%s", user.id)
        return access_token

    async def get_user(self, user_id: int):
        user = await self.db.users.get_one_or_none(id=user_id)
        if user is None:
            raise ObjectNotFoundError("User not found")
        return user
