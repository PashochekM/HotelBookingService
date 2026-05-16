from sqlalchemy import select

from src.models.users import UsersOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import UserDataMapper
from src.schemas.users import UserWithHashedPassword


class UsersRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed(self, email: str) -> UserWithHashedPassword | None:
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if not res:
            return None
        return UserWithHashedPassword.model_validate(res, from_attributes=True)
