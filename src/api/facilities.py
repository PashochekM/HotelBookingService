
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependcencies import DBDep
from src.schemas.facilities import FacilityAdd



router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("")
async def create_facility(db: DBDep, facility_data: FacilityAdd):
    result = await db.facilities.add_one(facility_data)
    await db.commit()

    #test_task.delay()

    return {"data": result}
