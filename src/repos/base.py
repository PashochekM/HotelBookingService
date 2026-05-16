from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import IntegrityError

from src.exceptions import DatabaseIntegrityError, ObjectAlreadyExistsError, ObjectNotFoundError, RelatedObjectNotFoundError
from src.repos.mappers.base import DataMapper


class BaseRepository:
    model = BaseModel
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    def _object_name(self) -> str:
        return self.model.__name__.removesuffix("Orm")

    def _raise_integrity_error(self, exc: IntegrityError):
        detail = str(exc.orig).lower()
        if "unique" in detail or "duplicate" in detail:
            raise ObjectAlreadyExistsError(f"{self._object_name()} already exists") from exc
        if "foreign key" in detail:
            raise RelatedObjectNotFoundError("Related object not found") from exc
        raise DatabaseIntegrityError() from exc

    async def get_filtered(self, *filter, **filters):
        query = select(self.model).filter(*filter).filter_by(**filters)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if res is None:
            return None
        return self.mapper.map_to_domain_entity(res)

    async def get_one(self, **filters):
        res = await self.get_one_or_none(**filters)
        if res is None:
            raise ObjectNotFoundError(f"{self._object_name()} not found")
        return res

    async def add_one(self, data):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            self._raise_integrity_error(exc)
        res = result.scalars().one()
        return self.mapper.map_to_domain_entity(res)

    async def add_bulk(self, data: list[BaseModel]):
        if not data:
            return

        stmt = insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        # print(stmt.compile(compile_kwargs={"literal_binds": True}))
        try:
            await self.session.execute(stmt)
        except IntegrityError as exc:
            self._raise_integrity_error(exc)

    async def edit(self, data, patch: bool = False, **filters):
        stmt = update(self.model).filter_by(**filters).values(**data.model_dump(exclude_unset=patch))
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            self._raise_integrity_error(exc)
        if result.rowcount == 0:
            raise ObjectNotFoundError(f"{self._object_name()} not found")

    async def delete(self, **filters):
        stmt = delete(self.model).filter_by(**filters)
        try:
            result = await self.session.execute(stmt)
        except IntegrityError as exc:
            detail = str(exc.orig).lower()
            if "foreign key" in detail:
                raise DatabaseIntegrityError(f"{self._object_name()} has related records") from exc
            self._raise_integrity_error(exc)
        if filters and result.rowcount == 0:
            raise ObjectNotFoundError(f"{self._object_name()} not found")
