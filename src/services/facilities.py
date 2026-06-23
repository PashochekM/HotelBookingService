import logging

from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class FacilitiesService(BaseService):
    async def get_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        result = await self.db.facilities.add_one(facility_data)
        await self.db.commit()
        logger.info("facility_created facility_id=%s title=%s", result.id, result.title)
        return result
