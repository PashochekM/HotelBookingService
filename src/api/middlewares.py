import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from src.exceptions import AppError
from src.services.auth import AuthService

logger = logging.getLogger(__name__)


def get_user_id_from_request(request: Request) -> int | None:
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = AuthService.decode_auth_token(token)
    except AppError:
        return None

    user_id = payload.get("id")
    return user_id if isinstance(user_id, int) else None


async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    request.state.request_id = request_id
    start_time = perf_counter()
    status_code = 500
    response = None

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = (perf_counter() - start_time) * 1000
        user_id = get_user_id_from_request(request)
        if response is not None:
            response.headers["X-Request-ID"] = request_id

        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO

        logger.log(
            level,
            "http_request method=%s path=%s status_code=%s duration_ms=%.2f request_id=%s user_id=%s",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
            request_id,
            user_id,
        )
