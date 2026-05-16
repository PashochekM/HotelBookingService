from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependcencies import FacilitiesServiceDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_facilities(facilities_service: FacilitiesServiceDep):
    return await facilities_service.get_facilities()


@router.post("")
async def create_facility(facilities_service: FacilitiesServiceDep, facility_data: FacilityAdd):
    result = await facilities_service.create_facility(facility_data)

    # test_task.delay()

    return {"data": result}
