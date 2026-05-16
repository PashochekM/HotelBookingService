import logging

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependcencies import DBDep
from src.schemas.facilities import FacilityAdd

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("")
async def create_facility(db: DBDep, facility_data: FacilityAdd):
    result = await db.facilities.add_one(facility_data)
    await db.commit()
    logger.info("facility_created facility_id=%s title=%s", result.id, result.title)

    # test_task.delay()

    return {"data": result}
