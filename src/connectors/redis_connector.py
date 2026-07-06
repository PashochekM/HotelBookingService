import logging

import redis.asyncio as redis
from redis.exceptions import RedisError

from src.exceptions import InfrastructureError

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        try:
            self.redis = redis.Redis(host=self.host, port=self.port)
            await self.redis.ping()
            logger.info("redis_connected host=%s port=%s", self.host, self.port)
        except (OSError, RedisError) as exc:
            self.redis = None
            raise InfrastructureError("Could not connect to Redis") from exc

    async def ping(self):
        try:
            if self.redis is None:
                await self.connect()
            else:
                await self.redis.ping()
        except (OSError, RedisError) as exc:
            self.redis = None
            raise InfrastructureError("Redis is unavailable") from exc

    def _get_client(self):
        if self.redis is None:
            logger.warning("redis_not_connected")
            raise InfrastructureError("Redis is not connected")
        return self.redis

    async def set(self, key: str, value: str, expire: int = None):
        redis_client = self._get_client()
        if expire is None:
            await redis_client.set(key, value)
        else:
            await redis_client.set(key, value, ex=expire)

    async def get(self, key: str):
        return await self._get_client().get(key)

    async def delete(self, key: str):
        await self._get_client().delete(key)

    async def disconnect(self):
        if self.redis:
            try:
                await self.redis.close()
                logger.info("redis_disconnected")
            except RedisError:
                logger.exception("Could not close Redis connection")
