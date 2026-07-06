import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from src import redis_manager
from src.api.dependencies import DBDep
from src.exceptions import InfrastructureError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health():
    return {"status": "ok"}


@router.get("/db")
async def health_db(db: DBDep):
    try:
        await db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("database_healthcheck_failed", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": "Database is unavailable"},
        )
    return {"status": "ok", "database": "ok"}


@router.get("/redis")
async def health_redis():
    try:
        await redis_manager.ping()
    except InfrastructureError as exc:
        logger.warning("redis_healthcheck_failed", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": exc.message},
        )
    return {"status": "ok", "redis": "ok"}
