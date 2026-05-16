from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update

from src.repos.mappers.base import DataMapper


class BaseRepository:
    model = BaseModel
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filters):
        query = select(self.model).filter(*filter).filter_by(**filters)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if res is None:
            return None
        return self.mapper.map_to_domain_entity(res)

    async def add_one(self, data):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(stmt)
        res = result.scalars().one()
        return self.mapper.map_to_domain_entity(res)

    async def add_bulk(self, data: list[BaseModel]):
        if not data:
            return

        stmt = (
            insert(self.model)
            .values([item.model_dump() for item in data])
            .returning(self.model)
        )
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(stmt)

    async def edit(self, data, patch: bool = False, **filters):
        stmt = (
            update(self.model)
            .filter_by(**filters)
            .values(**data.model_dump(exclude_unset=patch))
        )
        await self.session.execute(stmt)

    async def delete(self, **filters):
        stmt = delete(self.model).filter_by(**filters)
        await self.session.execute(stmt)
