from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.api.dependencies import FacilitiesServiceDep
from src.schemas.facilities import Facility, FacilityAdd
from src.schemas.responses import DataResponse

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", response_model=DataResponse[list[Facility]])
@cache(expire=10)
async def get_facilities(facilities_service: FacilitiesServiceDep):
    facilities = await facilities_service.get_facilities()
    return {"data": facilities}


@router.post("", response_model=DataResponse[Facility])
async def create_facility(facilities_service: FacilitiesServiceDep, facility_data: FacilityAdd):
    result = await facilities_service.create_facility(facility_data)

    # test_task.delay()

    return {"data": result}
